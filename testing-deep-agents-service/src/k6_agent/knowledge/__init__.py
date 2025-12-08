"""Knowledge retrieval integration for K6 performance testing.

This module provides integration with external RAG (Retrieval-Augmented Generation)
knowledge bases to enhance the agent's capabilities in:
- Performance scenario design best practices
- K6 script writing patterns and optimizations
- Test result analysis methodologies
- Bottleneck identification and root cause analysis

Example:
    >>> from k6_agent.knowledge import KnowledgeClient, KnowledgeRetriever
    >>> 
    >>> client = KnowledgeClient(api_url="http://localhost:8000")
    >>> retriever = KnowledgeRetriever(client)
    >>> 
    >>> # Retrieve K6 best practices
    >>> results = await retriever.retrieve_k6_practices("load testing scenarios")
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjBRNWRnPT06NTQ3ZWUwZTc=

from k6_agent.knowledge.client import KnowledgeClient, QueryMode, QueryRequest, QueryResponse
from k6_agent.knowledge.retriever import (
    KnowledgeRetriever,
    create_knowledge_retrieval_tool,
    create_scenario_design_tool,
    create_script_optimization_tool,
    create_analysis_guide_tool,
    create_bottleneck_diagnosis_tool,
)

__all__ = [
    # Client
    "KnowledgeClient",
    "QueryMode",
    "QueryRequest",
    "QueryResponse",
    # Retriever
    "KnowledgeRetriever",
    # Tools
    "create_knowledge_retrieval_tool",
    "create_scenario_design_tool",
    "create_script_optimization_tool",
    "create_analysis_guide_tool",
    "create_bottleneck_diagnosis_tool",
]
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TjBRNWRnPT06NTQ3ZWUwZTc=

