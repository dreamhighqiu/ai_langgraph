"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# """Data Collection Agent Module.
#
# This module provides a LangGraph-based agent for collecting API data and storing it
# in a knowledge base through a three-node workflow:
#
# 1. Node 1: Fetch API addresses (from user input or auto-parsing)
# 2. Node 2: Parallel crawl API data using crawl4ai
# 3. Node 3: Parallel insert data into RAG knowledge base
#
# Example:
#     >>> from src.data_agent import create_data_collection_agent
#     >>> agent, rag_url, api_key = create_data_collection_agent(
#     ...     rag_api_url="http://localhost:8000"
#     ... )
#     >>> result = agent.invoke({
#     ...     "api_urls": ["https://example.com/api"],
#     ...     "rag_api_url": "http://localhost:8000"
#     ... })
# """
#
# from .agent import (
#     DataCollectionState,
#     APIEndpoint,
#     CrawledContent,
#     fetch_api_addresses,
#     crawl_api_data,
#     insert_to_knowledge_base,
#     create_data_collection_graph,
#     create_data_collection_agent,
# )
#
# __all__ = [
#     "DataCollectionState",
#     "APIEndpoint",
#     "CrawledContent",
#     "fetch_api_addresses",
#     "crawl_api_data",
#     "insert_to_knowledge_base",
#     "create_data_collection_graph",
#     "create_data_collection_agent",
# ]
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V0dwVE1nPT06MTU2YjEzOTg=
