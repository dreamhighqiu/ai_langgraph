"""
数据模型模块

定义API测试系统中使用的所有数据结构。
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
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

