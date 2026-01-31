import asyncio
import logging
from typing import Any

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain_core.messages import ToolMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.runtime import Runtime
from langgraph.types import Overwrite

from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

from ui_agent.automation.runtime_config import get_runtime_config
from ui_agent.automation.script_generator import (
    create_script_save_tool,
    create_java_suite_save_tool,
)
from ui_agent.automation.executor import create_playwright_executor_tool
from ui_agent.automation.report_parser import create_result_parser_tool
from ui_agent.automation.base64_filter import contains_base64, replace_base64_in_content
from ui_agent.llm import create_chat_model
from ui_agent.mcp.registry import get_chrome_mcp_tools
from ui_agent.tools.common import run_async


logger = logging.getLogger(__name__)


CHROME_SYSTEM_PROMPT = """You are a UI automation assistant.

Use Chrome MCP tools to explore the target web page and identify key user flows.
Generate Playwright Java automation code (PageObject + Helper + Test).
Prefer stable locators and match the reference style if provided.

When ready, call `save_playwright_java` with the generated Java code.
"""


def create_chrome_mcp_agent(enable_chart_tools: bool = False, debug: bool = False):
    cfg = get_runtime_config()
    model = create_chat_model(require_api_key=False)
    all_tools = []

    chrome_tools = []
    try:
        chrome_tools = run_async(get_chrome_mcp_tools())
        logger.info("Loaded %s Chrome MCP tools", len(chrome_tools))
    except Exception as exc:
        logger.warning("Failed to load Chrome MCP tools: %s", exc)
        chrome_tools = []
    all_tools.extend(chrome_tools)

    if enable_chart_tools:
        try:
            chart_client = MultiServerMCPClient(
                {
                    "mcp-server-chart": {
                        "transport": "stdio",
                        "command": cfg.chart_mcp_command,
                        "args": cfg.chart_mcp_args,
                    }
                }
            )
            chart_tools = run_async(chart_client.get_tools())
            all_tools.extend(chart_tools)
        except Exception as exc:
            logger.warning("Failed to load chart MCP tools: %s", exc)

    script_save_tool = create_script_save_tool()
    java_save_tool = create_java_suite_save_tool()
    executor_tool = create_playwright_executor_tool()
    parser_tool = create_result_parser_tool()
    all_tools.extend([script_save_tool, java_save_tool, executor_tool, parser_tool])

    @before_model
    def filter_base64_content(state: AgentState, _runtime: Runtime) -> dict[str, Any] | None:
        messages = state.get("messages", [])
        if not messages:
            return None

        modified = False
        new_messages = []
        for msg in messages:
            if msg.type == "tool":
                content = msg.content
                if contains_base64(content):
                    message_id = msg.tool_call_id or msg.id or "unknown"
                    new_content = replace_base64_in_content(content, message_id)
                    new_msg = ToolMessage(
                        content=new_content,
                        tool_call_id=msg.tool_call_id,
                        name=getattr(msg, "name", None),
                        id=msg.id,
                    )
                    new_messages.append(new_msg)
                    modified = True
                else:
                    new_messages.append(msg)
            else:
                new_messages.append(msg)

        if modified:
            return {"messages": Overwrite(new_messages)}
        return None

    workspace_root = cfg.workspace_root
    backend = FilesystemBackend(root_dir=workspace_root, virtual_mode=True)

    agent = create_deep_agent(
        model=model,
        tools=all_tools,
        system_prompt=CHROME_SYSTEM_PROMPT,
        middleware=[filter_base64_content],
        backend=backend,
        debug=debug,
    )
    return agent
