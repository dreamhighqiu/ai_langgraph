"""MCP工具集成 - RAG知识检索和Chart图表生成."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import asyncio
from typing import Any

from langchain_core.tools import BaseTool
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZWtSVldnPT06YTI3NzFhMjE=

from k6_agent.config import K6Config, DEFAULT_CONFIG

# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZWtSVldnPT06YTI3NzFhMjE=

def get_rag_tools(config: K6Config | None = None) -> list[BaseTool]:
    """获取RAG MCP工具.
    
    Args:
        config: K6配置，默认使用DEFAULT_CONFIG
        
    Returns:
        RAG工具列表
    """
    cfg = config or DEFAULT_CONFIG
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
        
        client = MultiServerMCPClient({
            "rag-server": {
                "url": cfg.rag_mcp_url,
                "transport": "sse",
            }
        })
        
        tools = asyncio.run(client.get_tools())
        return list(tools)
    except Exception as e:
        print(f"Warning: Failed to load RAG MCP tools: {e}")
        return []


def get_chart_tools(config: K6Config | None = None) -> list[BaseTool]:
    """获取Chart MCP工具.
    
    Args:
        config: K6配置，默认使用DEFAULT_CONFIG
        
    Returns:
        Chart工具列表
    """
    cfg = config or DEFAULT_CONFIG
    
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZWtSVldnPT06YTI3NzFhMjE=
        
        client = MultiServerMCPClient({
            "chart-server": {
                "command": cfg.chart_mcp_command,
                "args": cfg.chart_mcp_args,
                "transport": "stdio",
            }
        })
        
        tools = asyncio.run(client.get_tools())
        return list(tools)
    except Exception as e:
        print(f"Warning: Failed to load Chart MCP tools: {e}")
        return []

def get_login_tools(config: K6Config | None = None) -> list[BaseTool]:
    """获取登录工具.

    Args:
        config: K6配置，默认使用DEFAULT_CONFIG

    Returns:
        登录工具列表
    """
    cfg = config or DEFAULT_CONFIG

    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZWtSVldnPT06YTI3NzFhMjE=

        client = MultiServerMCPClient({
            "login-server": {
                "url": cfg.login_mcp_url,
                "transport": "sse",
            }
        })
        tools = asyncio.run(client.get_tools())
        return list(tools)
    except Exception as e:
        print(f"Warning: Failed to load Login MCP tools: {e}")
        return []
def get_all_mcp_tools(config: K6Config | None = None) -> list[BaseTool]:
    """获取所有MCP工具.
    
    Args:
        config: K6配置
        
    Returns:
        所有MCP工具列表
    """
    tools = []
    # tools.extend(get_login_tools(config))
    tools.extend(get_rag_tools(config))
    tools.extend(get_chart_tools(config))
    return tools

