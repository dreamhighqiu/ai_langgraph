"""
MCP 服务器统一配置管理

本模块集中管理所有 MCP 服务器的配置，避免硬编码和配置分散。

MCP 服务器列表:
1. automation_quality - API/浏览器自动化 (stdio)
2. rag_query - LightRAG 查询服务 (SSE, Port 8002)
3. rag_anything - 文档处理 + 多模态查询 (SSE, Port 8001/8006)
4. pytest_mcp - Pytest 测试服务 (SSE, Port 8004)
5. playwright - UI 测试服务 (stdio)
6. midscene - Midscene 浏览器自动化 (stdio)
7. chrome_mcp - Chrome 控制 (SSE)
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def get_project_root() -> Path:
    """获取项目根目录 (testing-agents-service)"""
    return Path(__file__).parent.parent.resolve()


class MCPSettings(BaseSettings):
    """MCP 服务器统一配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # ========== automation_quality MCP (stdio) ==========
    automation_quality_enabled: bool = True
    automation_quality_command: str = "node"
    automation_quality_output_dir: str = "./api-test-reports"
    
    @property
    def automation_quality_server_path(self) -> str:
        """automation_quality MCP 服务器脚本路径"""
        return str(get_project_root() / "mcp" / "automation_quality" / "mcpServer.js")
    
    def get_automation_quality_config(self, api_only: bool = False) -> Dict[str, Any]:
        """获取 automation_quality MCP 配置"""
        args = [self.automation_quality_server_path]
        if api_only:
            args.append("--api-only")
        return {
            "transport": "stdio",
            "command": self.automation_quality_command,
            "args": args,
            "env": {
                "NODE_ENV": "production",
                "OUTPUT_DIR": self.automation_quality_output_dir,
            }
        }
    
    # ========== RAG Query MCP (SSE) ==========
    rag_query_enabled: bool = True
    rag_query_url: str = Field(
        default=os.getenv("RAG_QUERY_MCP_URL", "http://127.0.0.1:8002/sse"),
        description="RAG Query MCP 服务地址（支持环境变量 RAG_QUERY_MCP_URL）"
    )
    
    def get_rag_query_config(self) -> Dict[str, Any]:
        """获取 RAG Query MCP 配置"""
        return {
            "transport": "sse",
            "url": self.rag_query_url,
        }
    
    # ========== RAG Anything MCP (SSE) ==========
    rag_anything_enabled: bool = True
    rag_anything_url: str = Field(
        default=os.getenv("RAG_ANYTHING_MCP_URL", "http://localhost:8001/sse"),
        description="RAG Anything MCP 服务地址（支持环境变量 RAG_ANYTHING_MCP_URL，默认端口 8001）"
    )
    
    def get_rag_anything_config(self) -> Dict[str, Any]:
        """获取 RAG Anything MCP 配置"""
        return {
            "transport": "sse",
            "url": self.rag_anything_url,
        }
    
    # ========== Pytest MCP (SSE) ==========
    pytest_mcp_enabled: bool = True
    pytest_mcp_url: str = Field(
        default=os.getenv("PYTEST_MCP_URL", "http://127.0.0.1:8004/sse"),
        description="Pytest MCP 服务地址（支持环境变量 PYTEST_MCP_URL）"
    )
    
    def get_pytest_mcp_config(self) -> Dict[str, Any]:
        """获取 Pytest MCP 配置"""
        return {
            "transport": "sse",
            "url": self.pytest_mcp_url,
        }
    
    # ========== Playwright MCP (stdio) ==========
    playwright_mcp_enabled: bool = True
    playwright_mcp_command: str = "npx"
    playwright_mcp_args: list = ["-y", "@playwright/mcp@latest"]
    
    def get_playwright_mcp_config(self) -> Dict[str, Any]:
        """获取 Playwright MCP 配置"""
        return {
            "transport": "stdio",
            "command": self.playwright_mcp_command,
            "args": self.playwright_mcp_args,
        }
    
    # ========== Midscene MCP (stdio) ==========
    midscene_mcp_enabled: bool = True
    midscene_mcp_command: str = "npx"
    midscene_mcp_args: list = ["-y", "@midscene/web-bridge-mcp"]
    midscene_model_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    midscene_model_api_key: str = ""
    midscene_model_name: str = "doubao-seed-1-8-251215"
    midscene_model_family: str = "doubao-vision"
    midscene_request_timeout: str = "600000"
    
    def get_midscene_mcp_config(self) -> Dict[str, Any]:
        """获取 Midscene MCP 配置"""
        return {
            "transport": "stdio",
            "command": self.midscene_mcp_command,
            "args": self.midscene_mcp_args,
            "env": {
                "MIDSCENE_MODEL_BASE_URL": self.midscene_model_base_url,
                "MIDSCENE_MODEL_API_KEY": self.midscene_model_api_key,
                "MIDSCENE_MODEL_NAME": self.midscene_model_name,
                "MIDSCENE_MODEL_FAMILY": self.midscene_model_family,
                "MCP_SERVER_REQUEST_TIMEOUT": self.midscene_request_timeout,
            }
        }
    
    # ========== Chrome MCP (SSE) ==========
    chrome_mcp_enabled: bool = True
    chrome_mcp_transport: str = "sse"
    chrome_mcp_url: str = Field(
        default="http://localhost:9222/sse",
        description="Chrome MCP 服务地址"
    )
    
    def get_chrome_mcp_config(self) -> Dict[str, Any]:
        """获取 Chrome MCP 配置"""
        return {
            "transport": self.chrome_mcp_transport,
            "url": self.chrome_mcp_url,
        }


@lru_cache
def get_mcp_settings() -> MCPSettings:
    """获取 MCP 配置单例"""
    return MCPSettings()


# 便捷访问
mcp_settings = get_mcp_settings()

