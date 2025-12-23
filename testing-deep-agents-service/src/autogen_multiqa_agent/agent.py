from deepagents import create_deep_agent

from core.llms import deepseek_model
from knowledge_agent.tools import knowledge_tools
from autogen_requirements_agent.tools import analyze_requirement_document
from autogen_testcase_agent.tools import expand_testcases_from_requirements

SYSTEM_PROMPT = """你是一名多智能体协调助手，可同时处理知识检索、需求解析、测试规划：
- 当问题涉及现有知识库/文档时，优先使用 knowledge_tools 中的工具
- 用户上传的需求文档可调用 analyze_requirement_document
- 生成测试建议时，调用 expand_testcases_from_requirements
- 要求全局跟踪上下文，给出最终汇总答案
"""

agent = create_deep_agent(
    model=deepseek_model,
    tools=knowledge_tools
    + [analyze_requirement_document, expand_testcases_from_requirements],
    system_prompt=SYSTEM_PROMPT,
)
