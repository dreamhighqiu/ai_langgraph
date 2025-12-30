"""
API自动化测试Agent模块

基于DeepAgents框架的智能API测试自动化系统，集成MCP服务器提供工具功能。

主要组件：
- core: 核心模块（配置、编排器）
- agents: Agent定义
- models: 数据模型和类型定义
- prompts: Agent提示词模板
- mcp_servers: MCP服务器模块
    - pytest_generator: pytest测试生成器
    - test_executor: 测试执行器

目录结构：
    api_agent/
    ├── __init__.py
    ├── rag_api_agent.py              # 主入口
    ├── core/                # 核心模块
    │   ├── config.py        # 配置管理
    │   └── orchestrator.py  # Agent编排器
    ├── agents/              # Agent定义
    │   └── definitions.py   # SubAgent定义
    ├── models/              # 数据模型
    │   └── schemas.py       # Pydantic模型
    ├── prompts/             # 提示词
    │   └── templates.py     # 系统提示词模板
    └── mcp_servers/         # MCP服务器
        ├── pytest_generator.py  # pytest生成器
        └── test_executor.py     # 测试执行器
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vkc1a2RBPT06YTQ4MmE0MzI=

__version__ = "1.0.0"
__author__ = "API Agent Team"
# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vkc1a2RBPT06YTQ4MmE0MzI=

# 从新的模块结构导入
from .models.schemas import (
    HttpMethod,
    TestStatus,
    TestPriority,
    TestType,
    APIParameter,
    APIEndpoint,
    APISpec,
    TestAssertion,
    TestStep,
    TestCase,
    TestSuite,
    TestPlan,
    SuiteResult,
    GenerationResult,
    AgentSession,
)
# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vkc1a2RBPT06YTQ4MmE0MzI=

from .core.config import AgentConfig, get_config
from .core.orchestrator import APITestOrchestrator, create_api_test_agent

__all__ = [
    # Version
    "__version__",
    # Models
    "HttpMethod",
    "TestStatus",
    "TestPriority",
    "TestType",
    "APIParameter",
    "APIEndpoint",
    "APISpec",
    "TestAssertion",
    "TestStep",
    "TestCase",
    "TestSuite",
    "TestPlan",
    "SuiteResult",
    "GenerationResult",
    "AgentSession",
    # Config
    "AgentConfig",
    "get_config",
    # Orchestrator
    "APITestOrchestrator",
    "create_api_test_agent",
]
# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Vkc1a2RBPT06YTQ4MmE0MzI=
