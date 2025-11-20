"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langchain.agents import create_agent
from rag.chat.llms import deepseek_model
from rag.chat.tools import get_mcp_rag_tools, get_available_collections
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V0RkRFVBPT06ODMzZjkzNzc=

tools = [get_available_collections] + get_mcp_rag_tools()
agent = create_agent(model=deepseek_model(),
                     tools=tools,
                     system_prompt="根据用户的问题从合适的集合中查询相关知识。"
                                   "如果不确定当前使用的collection_name，可以使用 get_available_collections 工具获取所有可用的集合信息，"
                                   "然后根据集合的描述和用户的问题选择最合适的 collection_name。"
                     )