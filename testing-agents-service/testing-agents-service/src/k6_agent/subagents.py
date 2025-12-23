"""K6性能测试子智能体定义."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.tools import BaseTool
# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWt4T1JnPT06Y2FjZGQ2OGM=

from deepagents import SubAgent
from k6_agent.prompts import (
    RAG_SUBAGENT_PROMPT,
    SCRIPT_SUBAGENT_PROMPT,
    ANALYZER_SUBAGENT_PROMPT,
    REPORT_SUBAGENT_PROMPT,
)


def create_rag_subagent(
    rag_tools: list[BaseTool],
    model: BaseChatModel | None = None,
) -> SubAgent:
    """创建知识检索子智能体.
    
    Args:
        rag_tools: RAG MCP工具列表
        model: 语言模型（可选）
        
    Returns:
        知识检索子智能体定义
    """
    subagent: SubAgent = {
        "name": "rag-retrieval",
        "description": "使用此智能体从知识库中检索API接口信息、测试配置和历史数据。当需要了解接口详情、认证方式、请求参数等信息时使用。",
        "system_prompt": RAG_SUBAGENT_PROMPT,
        "tools": rag_tools,
    }
    if model:
        subagent["model"] = model
    return subagent

# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWt4T1JnPT06Y2FjZGQ2OGM=

def create_script_subagent(
    tools: list[BaseTool],
    model: BaseChatModel | None = None,
) -> SubAgent:
    """创建脚本生成子智能体.
    
    Args:
        tools: 工具列表（包含脚本保存工具）
        model: 语言模型（可选）
        
    Returns:
        脚本生成子智能体定义
    """
    subagent: SubAgent = {
        "name": "script-generator",
        "description": "使用此智能体生成K6性能测试脚本。需要提供API信息和测试需求，将生成完整可执行的K6脚本。",
        "system_prompt": SCRIPT_SUBAGENT_PROMPT,
        "tools": tools,
    }
    if model:
        subagent["model"] = model
    return subagent


def create_analyzer_subagent(
    tools: list[BaseTool],
    model: BaseChatModel | None = None,
) -> SubAgent:
    """创建性能分析子智能体.
    
    Args:
        tools: 工具列表
        model: 语言模型（可选）
        
    Returns:
        性能分析子智能体定义
    """
    subagent: SubAgent = {
        "name": "performance-analyzer",
        "description": "使用此智能体分析K6测试结果。将深度分析性能指标、识别瓶颈并给出优化建议。",
        "system_prompt": ANALYZER_SUBAGENT_PROMPT,
        "tools": tools,
    }
    if model:
        subagent["model"] = model
    return subagent

# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWt4T1JnPT06Y2FjZGQ2OGM=

def create_report_subagent(
    chart_tools: list[BaseTool],
    model: BaseChatModel | None = None,
) -> SubAgent:
    """创建报告生成子智能体.
    
    Args:
        chart_tools: Chart MCP工具列表
        model: 语言模型（可选）
        
    Returns:
        报告生成子智能体定义
    """
    subagent: SubAgent = {
        "name": "report-generator",
        "description": "使用此智能体生成性能测试报告。将根据测试结果和分析数据生成包含图表的专业Markdown报告。",
        "system_prompt": REPORT_SUBAGENT_PROMPT,
        "tools": chart_tools,
    }
    if model:
        subagent["model"] = model
    return subagent


def create_all_subagents(
    rag_tools: list[BaseTool],
    chart_tools: list[BaseTool],
    script_tools: list[BaseTool],
    analyzer_tools: list[BaseTool],
    model: BaseChatModel | None = None,
) -> list[SubAgent]:
    """创建所有子智能体.
    
    Args:
        rag_tools: RAG MCP工具
        chart_tools: Chart MCP工具
        script_tools: 脚本相关工具
        analyzer_tools: 分析相关工具
        model: 语言模型（可选）
        
    Returns:
        所有子智能体列表
    """
    return [
        create_rag_subagent(rag_tools, model),
        create_script_subagent(script_tools, model),
        create_analyzer_subagent(analyzer_tools, model),
        create_report_subagent(chart_tools, model),
    ]
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWt4T1JnPT06Y2FjZGQ2OGM=

