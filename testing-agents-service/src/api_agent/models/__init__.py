"""
数据模型模块

定义API测试系统中使用的所有数据结构。
"""


# pylint: disable  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtOYVdnPT06YTIwZmQ0YzA=

from api_agent.models.schemas import (
    # 枚举类型
    HttpMethod,
    TestStatus,
    TestPriority,
    TestType,
    # API模型
    APIParameter,
    APIEndpoint,
    APISpec,
    # 测试用例模型
    TestAssertion,
    TestStep,
    TestCase,
    TestSuite,
    # 测试计划模型
    TestPlanSection,
    TestPlan,
    # 执行结果模型
    StepResult,
    CaseResult,
    SuiteResult,
    # 代码生成模型
    GeneratedTestFile,
    GenerationResult,
    # 会话模型
    AgentSession,
)
# fmt: off  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtOYVdnPT06YTIwZmQ0YzA=

__all__ = [
    # 枚举类型
    "HttpMethod",
    "TestStatus",
    "TestPriority",
    "TestType",
    # API模型
    "APIParameter",
    "APIEndpoint",
    "APISpec",
    # 测试用例模型
    "TestAssertion",
    "TestStep",
    "TestCase",
    "TestSuite",
    # 测试计划模型
    "TestPlanSection",
    "TestPlan",
    # 执行结果模型
    "StepResult",
    "CaseResult",
    "SuiteResult",
    # 代码生成模型
    "GeneratedTestFile",
    "GenerationResult",
    # 会话模型
    "AgentSession",
]
# pragma: no cover  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WWtOYVdnPT06YTIwZmQ0YzA=

