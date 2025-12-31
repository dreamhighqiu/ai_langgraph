"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

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
        "url": "http://localhost:8002/sse",
        "transport": "sse",
    }
})
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVZkdmRBPT06MDQxMjQ4YWI=

tools = asyncio.run(client.get_tools())
agent = create_agent(model=llm, tools=tools)
