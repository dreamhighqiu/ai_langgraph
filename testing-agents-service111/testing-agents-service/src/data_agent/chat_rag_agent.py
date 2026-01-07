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

logger = logging.getLogger(__name__)

# Demo key; override via environment in real usage.
os.environ.setdefault("DEEPSEEK_API_KEY", "sk-0292e5a35e064f6f86169a20e39f0749")
llm = init_chat_model("deepseek:deepseek-chat")


def _load_mcp_tools():
    """Load MCP tools; return empty list if servers are down."""
    rag_mcp_url = os.environ.get("RAG_MCP_URL")  # legacy RAG MCP (optional)
    anything_rag_url = os.environ.get("ANYTHING_RAG_MCP_URL", "http://localhost:8006/sse")  # new LightRAG HTTP MCP
    try:
        servers = {
            "anything-rag-mcp": {"url": anything_rag_url, "transport": "sse"},
        }
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
