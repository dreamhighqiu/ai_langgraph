"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5oRVR3PT06YzExMTYzMTM=

from rag.chat.llms import deepseek_model

@tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VW5oRVR3PT06YzExMTYzMTM=

client = MultiServerMCPClient(
    {
        "mcp-server-rag": {
            "url": "http://127.0.0.1:8000/sse",
            "transport": "sse",
        }
    }
)
tools = asyncio.run(client.get_tools())
print(tools)
#
agent = create_agent(model=deepseek_model(),
                     tools=[add]
                     )