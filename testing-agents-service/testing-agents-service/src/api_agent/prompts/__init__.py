"""
提示词模块

定义Agent系统提示词和模板。
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# type: ignore  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDFWUE1nPT06MTUxYWM3MDM=

from api_agent.prompts.templates import (
    # 主Agent提示词
    ORCHESTRATOR_SYSTEM_PROMPT,
    # 子Agent提示词
    PLANNER_SYSTEM_PROMPT,
    GENERATOR_SYSTEM_PROMPT,
    EXECUTOR_SYSTEM_PROMPT,
    ANALYZER_SYSTEM_PROMPT,
)

__all__ = [
    "ORCHESTRATOR_SYSTEM_PROMPT",
    "PLANNER_SYSTEM_PROMPT",
    "GENERATOR_SYSTEM_PROMPT",
    "EXECUTOR_SYSTEM_PROMPT",
    "ANALYZER_SYSTEM_PROMPT",
]

# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDFWUE1nPT06MTUxYWM3MDM=
