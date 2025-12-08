

# System prompt to steer the agent to be an expert researcher
import asyncio
import os
# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1RCSVp3PT06OGRkN2Y3YmQ=

from deepagents import create_deep_agent
from langchain_deepseek import ChatDeepSeek
from langchain_mcp_adapters.client import MultiServerMCPClient

# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1RCSVp3PT06OGRkN2Y3YmQ=

client = MultiServerMCPClient(
    {
        "research": {
            "transport": "streamable_http",  # HTTP-based remote server
            "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=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",
        }
    }
)
tools = asyncio.run(client.get_tools())
research_instructions = """You are an expert researcher. Your job is to conduct thorough research and then write a polished report.

Use this to run an internet search for a given query. You can specify the max number of results to return, the topic, and whether raw content should be included.
"""
os.environ["DEEPSEEK_API_KEY"] = "sk-ab8dda459d2a4203b71c6aa2065b411a"
deepseek = ChatDeepSeek(model="deepseek-chat")

agent = create_deep_agent(
    model=deepseek,
    tools=tools,
    system_prompt=research_instructions
)