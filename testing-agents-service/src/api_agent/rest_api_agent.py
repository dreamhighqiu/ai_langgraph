

import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent as create_agent
from config.mcp_settings import mcp_settings
from config.llm_config import get_llm
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

# 初始化 DeepSeek 模型（此 Agent 专用 DeepSeek）
model = get_llm(provider="deepseek", model_name="deepseek-chat")
# DeepSeek chat has a 131072 token context window; set the profile so the deepagents
# summarization middleware can trim history before we hit the hard limit.
model.profile = {"max_input_tokens": 131072}
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

# 使用统一的 MCP 配置
client = MultiServerMCPClient(
    {
        "automation-quality": mcp_settings.get_automation_quality_config()
    }
)
tools = asyncio.run(client.get_tools())
agent = create_agent(model=model, tools=tools)
