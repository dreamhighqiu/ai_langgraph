"""
Chat RAG Agent - loads MCP tools to query LightRAG via rag-server (legacy) and
anything-rag-mcp (new HTTP wrapper).
"""

import asyncio
import logging

from langchain.agents import create_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from config.mcp_settings import mcp_settings
from config.llm_config import get_llm_model

logger = logging.getLogger(__name__)

# 使用统一的 LLM 配置（从 settings.py 读取）
llm = get_llm_model()


def _load_mcp_tools():
    """Load MCP tools; return empty list if servers are down."""
    try:
        # 使用统一的 MCP 配置
        servers = {
            "anything-rag-mcp": mcp_settings.get_rag_anything_config(),
        }
        
        # 如果 RAG Query 服务也启用，添加到服务器列表
        if mcp_settings.rag_query_enabled:
            servers["rag-query-mcp"] = mcp_settings.get_rag_query_config()

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
