
import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from deepagents import create_deep_agent
from langchain_core.runnables import RunnableConfig
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.pregel import Pregel
from config.mcp_settings import mcp_settings
from config.llm_config import get_llm_model
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjJKWWNBPT06ZGEzZGJmNDg=

# 定义系统提示词
SYSTEM_PROMPT = """你是一个专业的Web自动化测试助手，可以使用Playwright来控制浏览器完成各种任务。

你可以：
- 打开网页
- 点击元素
- 填写表单
- 截图
- 等待元素加载
- 执行JavaScript代码

请根据用户的指令，使用提供的工具来完成浏览器自动化任务。
"""
# model = init_chat_model("deepseek:deepseek-chat")
# client = MultiServerMCPClient(
#     {
#         "midscene-web": {
#             "transport": "stdio",
#             "command": "npx",
#             "args": ["-y", "@playwright/mcp@latest"],
#         }
#     }
# )
# tools = asyncio.run(client.get_tools())
# agent = create_deep_agent(
#     tools=tools,
#     system_prompt=SYSTEM_PROMPT,
#     model=model,
# )
#
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjJKWWNBPT06ZGEzZGJmNDg=


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
            "playwright": mcp_settings.get_playwright_mcp_config()
        }
    )

    # 使用 async with 保持 session 存活
    async with client.session("playwright") as session:
        # 在 session 中加载 tools
        tools = await load_mcp_tools(session)
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjJKWWNBPT06ZGEzZGJmNDg=

        # 使用统一的 LLM 配置
        model = get_llm_model()

        # 创建 agent (注意: tools 和 instructions 是位置参数)
        agent = create_deep_agent(
            tools=tools,
            system_prompt=SYSTEM_PROMPT,
            model=model,
        )

        # yield agent，session 会保持存活直到请求处理完成
        yield agent


# 导出 make_agent 供 LangGraph API 使用
agent = make_agent
# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjJKWWNBPT06ZGEzZGJmNDg=

