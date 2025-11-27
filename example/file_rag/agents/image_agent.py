"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from langchain.agents import create_agent
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZvMVpBPT06YzM1ZWZiMmY=

from file_rag.core.llms import image_llm_model
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2YVZvMVpBPT06YzM1ZWZiMmY=

agent = create_agent(
    model=image_llm_model,
    tools=[],
    system_prompt="你是AI智能助手，专门针对用户上传的图片，回答用户问题。请仔细分析图片内容并提供详细的回答。",
    name="image_chat_agent",
)