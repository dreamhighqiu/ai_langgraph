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
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oTVlRPT06YjVmODE4NzE=

os.environ["DEEPSEEK_API_KEY"] = "sk-9f51590e5d464509ad731fa8aea89f16"
llm = init_chat_model("deepseek:deepseek-chat")
client = MultiServerMCPClient({
    "rag-server": {
        "url": "http://localhost:8002/sse",
        "transport": "sse",
    }
})

tools = asyncio.run(client.get_tools())
agent = create_agent(model=llm, tools=tools)
# fmt: off  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oTVlRPT06YjVmODE4NzE=
