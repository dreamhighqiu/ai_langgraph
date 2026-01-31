"""
Chat RAG Agent - loads MCP tools to query LightRAG via rag-server (legacy) and
anything-rag-mcp (new HTTP wrapper).
"""

import asyncio
import logging
import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from config.mcp_settings import mcp_settings

logger = logging.getLogger(__name__)

# Demo key; override via environment in real usage.
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-0292e5a35e064f6f86169a20e39f0749")
llm = init_chat_model("deepseek:deepseek-chat")


def _load_mcp_tools():
    """Load MCP tools; return empty list if servers are down."""
    try:
        # 使用统一的 MCP 配置
        servers = {
            "anything-rag-mcp": mcp_settings.get_rag_anything_config(),
        }
        
        # 如果 RAG Query 服务也启用，添加到服务器列表
        if mcp_settings.rag_query_enabled:
            rag_mcp_url = os.environ.get("RAG_MCP_URL")  # 允许环境变量覆盖
            if rag_mcp_url:
                servers["rag-server"] = {"url": rag_mcp_url, "transport": "sse"}

        client = MultiServerMCPClient(servers)
        tools = asyncio.run(client.get_tools())
        logger.info("Loaded %s MCP tools from %s", len(tools), list(servers.keys()))
        return list(tools)
    except Exception as exc:  # pylint: disable=broad-except
        logger.warning(
            "Cannot load MCP tools (server may be down or misconfigured): %s; using empty tool list",
            exc,
        )
        return []


tools = _load_mcp_tools()

SYSTEM_PROMPT = """
You are the enterprise RAG assistant.
Always call available MCP tools first (anything-rag-mcp.query_text/query_data or rag-server.query/...)
to retrieve grounded context before answering.
If tools are unavailable or return empty/without references, reply exactly: 无法获取到知识库信息.
Do not speculate or answer from prior knowledge. Keep responses concise and grounded in retrieved facts.
"""

agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
