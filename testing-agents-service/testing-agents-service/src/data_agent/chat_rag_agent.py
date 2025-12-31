"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
import os
import logging

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oTVlRPT06YjVmODE4NzE=

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
llm = init_chat_model("deepseek:deepseek-chat")

# 尝试连接 MCP 服务器，如果失败则使用空工具列表
tools = []
try:
    client = MultiServerMCPClient({
        "rag-server": {
            "url": "http://localhost:8001/sse",
            "transport": "sse",
        }
    })
    tools = asyncio.run(client.get_tools())
    logger.info(f"Successfully loaded {len(tools)} tools from RAG MCP server")
    # 打印工具名称以便调试
    tool_names = [tool.name for tool in tools]
    logger.info(f"Available tools: {tool_names}")
except ExceptionGroup as eg:
    logger.warning(f"Failed to load RAG MCP tools (ExceptionGroup): {eg}. Creating agent without MCP tools.")
    tools = []
except Exception as e:
    logger.warning(f"Failed to load RAG MCP tools: {e}. Creating agent without MCP tools.")
    tools = []

# 创建 Agent 并添加系统提示，明确告诉 LLM 要使用工具
system_prompt = """你是一个知识库问答助手。当用户询问知识库中的信息时，你必须使用 query 工具来查询知识库。
重要提示：
1. 对于任何关于知识库内容的查询，必须调用 query 工具
2. 不要直接回答"知识库中没有相关信息"，必须先调用工具查询
3. 工具名称是 'query'，参数是 query_text（查询文本）和 mode（查询模式，默认使用 'hybrid'）
"""

agent = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
logger.info(f"Agent created with {len(tools)} tools")
# fmt: off  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y25oTVlRPT06YjVmODE4NzE=
