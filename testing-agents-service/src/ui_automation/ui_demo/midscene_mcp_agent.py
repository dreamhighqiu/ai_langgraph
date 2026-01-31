
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=

from deepagents import create_deep_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.pregel import Pregel
from config.mcp_settings import mcp_settings
from config.llm_config import get_llm_model


# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=

@asynccontextmanager
async def make_agent() -> AsyncIterator[Pregel]:
    """
    创建 agent 的工厂函数，使用 asynccontextmanager 保持 MCP session 存活。

    这是 LangGraph API 推荐的方式：
    - session 在 agent 生命周期内保持活跃
    - 退出时自动清理资源
    """

    # 使用统一的 MCP 配置
    client = MultiServerMCPClient(
        {
            "midscene-web": mcp_settings.get_midscene_mcp_config()
        }
    )

    # 使用 async with 保持 session 存活
    async with client.session("midscene-web") as session:
        # 在 session 中加载 tools
        tools = await load_mcp_tools(session)

        # 使用统一的 LLM 配置
        model = get_llm_model()

        # 创建 agent (注意: tools 和 instructions 是位置参数)
        agent = create_deep_agent(
            tools=tools,
            # system_prompt=SYSTEM_PROMPT,
            model=model,
        )
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=

        # yield agent，session 会保持存活直到请求处理完成
        yield agent


# 导出 make_agent 供 LangGraph API 使用
agent = make_agent

# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=
