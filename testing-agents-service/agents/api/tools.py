
import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient

from config.mcp_settings import mcp_settings

# 使用统一的 MCP 配置
client = MultiServerMCPClient(
    {
        "api": mcp_settings.get_automation_quality_config(api_only=True)
    }
)
api_tools = asyncio.run(client.get_tools())
