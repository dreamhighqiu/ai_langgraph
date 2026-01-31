

import asyncio

from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient(
    {
        "api": {
            "transport": "stdio",
            "command": "node",
            "args": [r".\mcp\automation_quality\mcpServer.js", "--api-only"],
            "env": {
                "NODE_ENV": "production",
                "OUTPUT_DIR": "./api-test-reports"
            }
        }
    }
)
api_tools = asyncio.run(client.get_tools())
