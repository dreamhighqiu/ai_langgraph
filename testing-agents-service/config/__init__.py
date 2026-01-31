"""
配置管理模块

包含应用配置和 MCP 服务器配置。
"""

from config.settings import settings, get_settings
from config.mcp_settings import mcp_settings, get_mcp_settings

__all__ = [
    "settings",
    "get_settings",
    "mcp_settings",
    "get_mcp_settings",
]

