"""Core components for K6 Performance Testing Agent.

This module provides the core framework components including:
- Agent orchestration and creation
- Configuration management
- System prompts for agents
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from k6_agent.core.config import (
    K6AgentConfig,
    K6Config,
    Environment,
    MonitoringConfig,
    ReportConfig,
    KnowledgeConfig,
)
from k6_agent.core.prompts import (
    ORCHESTRATOR_PROMPT,
    SCRIPT_GENERATOR_PROMPT,
    TEST_EXECUTOR_PROMPT,
    RESULT_ANALYZER_PROMPT,
    REPORT_GENERATOR_PROMPT,
)
# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VGUWNnPT06MzcxOGJmZDQ=

__all__ = [
    # Configuration
    "K6AgentConfig",
    "K6Config",
    "Environment",
    "MonitoringConfig",
    "ReportConfig",
    "KnowledgeConfig",
    # Prompts
    "ORCHESTRATOR_PROMPT",
    "SCRIPT_GENERATOR_PROMPT",
    "TEST_EXECUTOR_PROMPT",
    "RESULT_ANALYZER_PROMPT",
    "REPORT_GENERATOR_PROMPT",
]
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VGUWNnPT06MzcxOGJmZDQ=

