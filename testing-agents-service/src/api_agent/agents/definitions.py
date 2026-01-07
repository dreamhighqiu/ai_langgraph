"""
子Agent定义模块

定义API测试系统中使用的专业化子Agent。
每个子Agent负责特定的任务领域。
"""


# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2xsWmFnPT06ZjJlZDc0NWM=

from typing import Sequence
from deepagents.middleware.subagents import SubAgent

from api_agent.prompts.templates import (
    RAG_RETRIEVAL_SYSTEM_PROMPT,
    PLANNER_SYSTEM_PROMPT,
    GENERATOR_SYSTEM_PROMPT,
    EXECUTOR_SYSTEM_PROMPT,
    ANALYZER_SYSTEM_PROMPT,
)


def get_rag_retrieval_agent() -> SubAgent:
    """
    获取RAG检索Agent定义

    职责：
    - 从知识库检索API接口信息
    - 提取接口的详细配置（URL、参数、认证等）
    - 查找历史测试数据和基准值

    Returns:
        SubAgent: RAG检索Agent规范
    """
    return SubAgent(
        name="rag-retrieval",
        description="""API接口知识检索专家Agent。负责从知识库中检索API接口的详细信息。

使用场景：
- 用户提到具体的API接口名称（如"首页接口"、"登录接口"）
- 需要了解接口的URL、参数、认证方式等详细信息
- 需要查找历史测试数据和基准值
- 在生成测试计划或测试脚本之前需要获取接口上下文

输入：接口名称或功能描述
输出：结构化的API接口信息（包括URL、Method、Headers、Body、认证方式、测试基准等）

⚠️ 重要：当用户提到任何具体的API接口时，应该优先调用此Agent获取接口信息""",
        system_prompt=RAG_RETRIEVAL_SYSTEM_PROMPT,
        tools=[],  # 使用主Agent的MCP工具（rag_query_data等）
    )

# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2xsWmFnPT06ZjJlZDc0NWM=

def get_test_planner_agent() -> SubAgent:
    """
    获取测试计划Agent定义
    
    职责：
    - 分析API文档（OpenAPI/Swagger）
    - 制定测试策略和计划
    - 设计测试用例和场景
    
    Returns:
        SubAgent: 测试计划Agent规范
    """
    return SubAgent(
        name="test-planner",
        description="""测试计划专家Agent。负责分析API文档并制定全面的测试计划。

使用场景：
- 用户提供API文档需要分析
- 需要制定测试策略和计划
- 需要设计测试用例和场景

输入：API文档内容或路径
输出：结构化的测试计划（JSON格式）""",
        system_prompt=PLANNER_SYSTEM_PROMPT,
        tools=[],  # 使用主Agent的MCP工具
    )


def get_test_generator_agent() -> SubAgent:
    """
    获取测试生成Agent定义
    
    职责：
    - 根据测试计划生成pytest测试代码
    - 集成Allure报告装饰器
    - 生成conftest.py和配置文件
    
    Returns:
        SubAgent: 测试生成Agent规范
    """
    return SubAgent(
        name="test-generator",
        description="""pytest测试代码生成专家Agent。负责生成高质量的pytest测试脚本。

使用场景：
- 需要根据测试计划生成测试代码
- 需要生成pytest配置文件
- 需要生成测试数据和fixtures

输入：测试计划或测试用例定义
输出：pytest测试文件、conftest.py、pytest.ini等

生成的代码特点：
- 使用pytest+requests框架
- 集成Allure报告装饰器
- 支持参数化测试
- 包含详细的步骤和断言""",
        system_prompt=GENERATOR_SYSTEM_PROMPT,
        tools=[],  # 使用主Agent的MCP工具
    )


def get_test_executor_agent() -> SubAgent:
    """
    获取测试执行Agent定义
    
    职责：
    - 执行pytest测试（支持并行）
    - 收集测试结果
    - 生成Allure报告
    
    Returns:
        SubAgent: 测试执行Agent规范
    """
    return SubAgent(
        name="test-executor",
        description="""测试执行专家Agent。负责执行pytest测试并收集结果。

使用场景：
- 需要执行已生成的测试脚本
- 需要并行执行大量测试
- 需要生成Allure HTML报告

输入：测试文件路径或目录
输出：测试执行结果和Allure报告

执行特点：
- 支持pytest-xdist并行执行
- 自动生成Allure JSON结果
- 可生成Allure HTML报告
- 支持失败重试""",
        system_prompt=EXECUTOR_SYSTEM_PROMPT,
        tools=[],  # 使用主Agent的MCP工具
    )
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2xsWmFnPT06ZjJlZDc0NWM=


def get_test_analyzer_agent() -> SubAgent:
    """
    获取结果分析Agent定义
    
    职责：
    - 分析测试执行结果
    - 识别失败模式
    - 生成分析报告
    
    Returns:
        SubAgent: 结果分析Agent规范
    """
    return SubAgent(
        name="test-analyzer",
        description="""测试结果分析专家Agent。负责分析测试结果并提供洞察。

使用场景：
- 需要分析测试执行结果
- 需要识别失败原因和模式
- 需要生成测试报告摘要

输入：测试结果文件或Allure结果目录
输出：分析报告（Markdown格式）

分析内容：
- 执行概览和统计
- 失败用例分析
- 根因识别
- 改进建议""",
        system_prompt=ANALYZER_SYSTEM_PROMPT,
        tools=[],  # 使用主Agent的MCP工具
    )


def get_all_subagents() -> Sequence[SubAgent]:
    """
    获取所有子Agent定义

    Returns:
        Sequence[SubAgent]: 所有子Agent的列表
    """
    return [
        get_rag_retrieval_agent(),  # RAG检索Agent - 优先级最高
        get_test_planner_agent(),
        get_test_generator_agent(),
        get_test_executor_agent(),
        get_test_analyzer_agent(),
    ]
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2xsWmFnPT06ZjJlZDc0NWM=

