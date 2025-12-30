"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=

from deepagents import create_deep_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.pregel import Pregel
#
# client = MultiServerMCPClient(
#     {
#         "midscene-web": {
#             "transport": "stdio",
#             "command": "npx",
#             "args": ["-y", "@midscene/web-bridge-mcp"],
#             "env": {
#                 "MIDSCENE_MODEL_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3",
#                 "MIDSCENE_MODEL_API_KEY": "sk-a7299a7df2904fe69c24a2ca98e8dca4",
#                 "MIDSCENE_MODEL_NAME": "doubao-seed-1-8-251215",
#                 "MIDSCENE_MODEL_FAMILY": "doubao-vision",
#                 "MCP_SERVER_REQUEST_TIMEOUT": "600000"
#             }
#         }
#     }
# )
os.environ["DEEPSEEK_API_KEY"] = "sk-a7299a7df2904fe69c24a2ca98e8dca4"
# model = init_chat_model("deepseek:deepseek-chat")
#
# tools = asyncio.run(client.get_tools())
# print(tools)
# agent = create_deep_agent(model=model, tools=tools)

# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U25SRWJnPT06N2M3NThmYjQ=

@asynccontextmanager
async def make_agent() -> AsyncIterator[Pregel]:
    """
    创建 agent 的工厂函数，使用 asynccontextmanager 保持 MCP session 存活。

    这是 LangGraph API 推荐的方式：
    - session 在 agent 生命周期内保持活跃
    - 退出时自动清理资源
    """

    client = MultiServerMCPClient(
        {
            "midscene-web": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@midscene/web-bridge-mcp"],
                "env": {
                    "MIDSCENE_MODEL_BASE_URL": "https://ark.cn-beijing.volces.com/api/v3",
                    "MIDSCENE_MODEL_API_KEY": "sk-a7299a7df2904fe69c24a2ca98e8dca4",
                    "MIDSCENE_MODEL_NAME": "doubao-seed-1-8-251215",
                    "MIDSCENE_MODEL_FAMILY": "doubao-vision",
                    "MCP_SERVER_REQUEST_TIMEOUT": "600000"
                }
            }
        }
    )

    # 使用 async with 保持 session 存活
    async with client.session("midscene-web") as session:
        # 在 session 中加载 tools
        tools = await load_mcp_tools(session)

        model = init_chat_model("deepseek:deepseek-chat")

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
