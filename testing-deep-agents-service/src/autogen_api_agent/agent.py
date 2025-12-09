from deepagents import create_deep_agent

from core.llms import deepseek_model
from .tools import design_api_spec, generate_api_test_plan

SYSTEM_PROMPT = """你是一名 API 设计与质量负责人。
- 当用户提供业务需求时，先调用 design_api_spec 生成结构化接口文档
- 如果用户需要测试计划或自动化建议，调用 generate_api_test_plan
- 输出需引用工具结果并给出总结
"""

agent = create_deep_agent(
    model=deepseek_model,
    tools=[design_api_spec, generate_api_test_plan],
    system_prompt=SYSTEM_PROMPT,
)
