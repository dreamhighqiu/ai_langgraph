"""
DeepAgent graph for requirement analysis and testcase generation.
"""

from deepagents import create_deep_agent

from core.llms import deepseek_model
from .tools import analyze_requirement_document, generate_testcases_from_requirements

SYSTEM_PROMPT = """你是企业级软件项目的高级需求&测试负责人。
你需要回答用户关于需求分析、测试覆盖、质量风险的所有问题，并善用可用的工具：
1. analyze_requirement_document —— 将原始需求文本解析为结构化 JSON
2. generate_testcases_from_requirements —— 根据结构化需求生成测试用例 JSON

工作原则：
- 当用户提供需求/PRD/会议纪要等文本时，优先调用 analyze_requirement_document 获取结构化结果
- 若用户需要测试用例或覆盖分析，使用 generate_testcases_from_requirements
- 如果已经得到 JSON 结果，可自行总结或再次调用工具深化答案
- 输出中文，并结合工具返回的数据给出专业建议
"""

agent = create_deep_agent(
    model=deepseek_model,
    tools=[analyze_requirement_document, generate_testcases_from_requirements],
    system_prompt=SYSTEM_PROMPT,
)
