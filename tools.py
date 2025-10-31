"""
工具模块 - 提供各种 MCP 工具的封装
添加了错误处理和延迟初始化机制
"""

import asyncio
from typing import List
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient


def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}，今天是晴天，温度为 25 摄氏度。"


def _safe_get_mcp_tools(client_config: dict, tool_name: str) -> List[BaseTool]:
    """
    安全地获取 MCP 工具，添加错误处理
    
    Args:
        client_config: MCP 客户端配置
        tool_name: 工具名称（用于日志）
    
    Returns:
        工具列表，如果失败则返回空列表
    """
    try:
        client = MultiServerMCPClient(client_config)
        tools = asyncio.run(client.get_tools())
        print(f"✓ 成功加载 {tool_name} 工具: {len(tools)} 个")
        return tools
    except Exception as e:
        print(f"✗ 加载 {tool_name} 工具失败: {str(e)}")
        return []


def get_tavily_search_mcp_tools() -> List[BaseTool]:
    """获取 Tavily 搜索 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "tavily_search": {
                "transport": "streamable_http",
                "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=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"
            }
        },
        "Tavily Search"
    )


# def playwright_mcp_local_tools() -> List[BaseTool]:
#     """获取 Playwright MCP 本地工具"""
#     return _safe_get_mcp_tools(
#         {
#             "playwright_mcp": {
#                 "transport": "stdio",
#                 "command": "npx",
#                 "args": ["@playwright/mcp@latest"]
#             }
#         },
#         "Playwright"
#     )


def chrome_mcp_local_tools() -> List[BaseTool]:
    """获取 Chrome MCP 本地工具"""
    return _safe_get_mcp_tools(
        {
            "chrome_mcp": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:12306/mcp"
            }
        },
        "Chrome"
    )


def chart_mcp_tools() -> List[BaseTool]:
    """获取图表 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "chart_mcp": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@antv/mcp-server-chart"]
            }
        },
        "Chart"
    )


# def filesystem_mcp_tools() -> List[BaseTool]:
#     """获取文件系统 MCP 工具"""
#     return _safe_get_mcp_tools(
#         {
#             "filesystem": {
#                 "args": [
#                     "-y",
#                     "@modelcontextprotocol/server-filesystem",
#                     "data/"
#                 ],
#                 "command": "npx",
#                 "transport": "stdio"
#             }
#         },
#         "Filesystem"
#     )

def filesystem_mcp_tools() -> List[BaseTool]:
    """获取文件系统 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "filesystem": {
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "data/"
                    "."
                ],
                "command": "npx",
                "transport": "stdio"
            }
        },
        "Filesystem"
    )

def excel_mcp_tools() -> List[BaseTool]:
    """获取 Excel MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "excel_mcp": {
                "args": [
                    "--yes",
                    "@negokaz/excel-mcp-server"
                ],
                "command": "npx",
                "transport": "stdio",
                "env": {
                    "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
                }
            }
        },
        "Excel"
    )


def markdown_mcp_tools() -> List[BaseTool]:
    """获取 Markdown MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "markdown_mcp": {
                "args": [
                    "/Users/qiuyunxia/code/ai_langGraph/markdownify-mcp/dist/index.js"
                ],
                "command": "node",
                "transport": "stdio",
                "env": {
                    "UV_PATH": "/opt/homebrew/bin/uv"
                }
            }
        },
        "Markdown"
    )


# 测试代码（取消注释以测试）
if __name__ == "__main__":
    print("测试工具加载...")
    print("\n1. 测试 Tavily Search:")
    get_tavily_search_mcp_tools()

    print("\n2. 测试 Chart:")
    chart_mcp_tools()

    print("\n3. 测试 Filesystem:")
    filesystem_mcp_tools()

# print(filesystem_mcp_tools())
