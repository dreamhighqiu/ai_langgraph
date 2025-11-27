"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langchain.agents import create_agent
from file_rag.core.llms import deepseek_model
# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um1KM1ZBPT06MjY1YmI5YmE=

# 根据需求的复杂度增加 中间件、工具等内容
agent = create_agent(
    model=deepseek_model,
    tools=[],
    system_prompt="你擅长基于用户提供的上下文信息回答用户问题。",
    name="chat_agent",
)