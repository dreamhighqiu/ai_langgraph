"""
聊天 RAG Agent - 通过 MCP 工具查询知识库
默认通过 RAG MCP Server (SSE) 与 LightRAG（Milvus 向量存储）交互。
"""

import asyncio
import logging
import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

logger = logging.getLogger(__name__)

# DeepSeek API key（示例密钥，生产请改为环境变量注入）
os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
llm = init_chat_model("deepseek:deepseek-chat")


def _load_mcp_tools():
    """加载 RAG MCP 工具；若 MCP 未启动则返回空列表。"""
    # 默认连 8001 的 mcp_server_rag_anything（Milvus），可通过 RAG_MCP_URL 覆盖
    rag_mcp_url = os.environ.get("RAG_MCP_URL", "http://localhost:8001/sse")
    try:
        client = MultiServerMCPClient({
            "rag-server": {
                # 对齐 start_all.sh 默认端口：8002；后台 rag_mcp_server 会转发到 LightRAG（Milvus）
                "url": rag_mcp_url,
                "transport": "sse",
            }
        })
        tools = asyncio.run(client.get_tools())
        logger.info(f"成功加载 {len(tools)} 个 RAG MCP 工具，地址：{rag_mcp_url}")
        return list(tools)
    except Exception as e:
        logger.warning(f"无法加载 RAG MCP 工具（可能未启动或端口配置错误）: {e}，将使用空工具列表创建 agent")
        return []


# 延迟加载工具，避免 import 时阻塞
tools = _load_mcp_tools()

# 系统提示：强制优先使用 RAG 工具检索，再回答
SYSTEM_PROMPT = """你是企业内部知识库助手。必须先调用可用的工具（rag-server.query 或 query_with_multimodal）从知识库检索相关内容，再给出回答。
除非工具不可用或检索为空，否则不要直接凭空回答。
回答时优先使用检索到的事实，并保持简洁。"""

agent = create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
