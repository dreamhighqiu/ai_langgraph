

import asyncio
import os

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVZkdmRBPT06MDQxMjQ4YWI=

os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
llm = init_chat_model("deepseek:deepseek-chat")
client = MultiServerMCPClient({
    "rag-server": {
        "url": "http://localhost:8001/sse",  # 使用 8001 端口的 RAG Anything MCP 服务器
        "transport": "sse",
    }
})
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVZkdmRBPT06MDQxMjQ4YWI=

tools = asyncio.run(client.get_tools())
agent = create_agent(model=llm, tools=tools)
