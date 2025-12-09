from deepagents import create_deep_agent

from core.llms import deepseek_model
from .tools import expand_testcases_from_requirements, review_testcases

SYSTEM_PROMPT = """你是端到端测试负责人，擅长将需求转换成覆盖全面的测试计划，并持续评审。

当用户提供需求/用例 JSON 时：
- expand_testcases_from_requirements：生成或补全测试用例
- review_testcases：审查覆盖度，指出缺口

输出中文，必要时引用工具返回 JSON。"""

agent = create_deep_agent(
    model=deepseek_model,
    tools=[expand_testcases_from_requirements, review_testcases],
    system_prompt=SYSTEM_PROMPT,
)
