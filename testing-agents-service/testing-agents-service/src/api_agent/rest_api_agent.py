"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
import os
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent as create_agent
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

os.environ["DEEPSEEK_API_KEY"] = "sk-868325fd211f4303a106658a98bb9aab"
model = init_chat_model("deepseek:deepseek-chat")
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

client = MultiServerMCPClient(
    {
        "automation-quality": {
            "transport": "stdio",
            "command": "npx",
            "args": [r"C:\Users\86134\Desktop\workspace\production\004\testing-agents-service\src\api_agent\mcp_servers\automation-quality-mcp"],
            "env": {
                "NODE_ENV": "production",
                "OUTPUT_DIR": "./api-test-reports"
            }
        }
    }
)
tools = asyncio.run(client.get_tools())
agent = create_agent(model=model, tools=tools)
