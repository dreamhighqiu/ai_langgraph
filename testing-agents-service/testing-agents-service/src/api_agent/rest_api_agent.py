

import asyncio
import os
from pathlib import Path
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent as create_agent
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
model = init_chat_model("deepseek:deepseek-chat")
# DeepSeek chat has a 131072 token context window; set the profile so the deepagents
# summarization middleware can trim history before we hit the hard limit.
model.profile = {"max_input_tokens": 131072}
# pragma: no cover  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZDNnMmVnPT06OWQ4NmJmNzg=

# Get the directory of this file and build relative path to automation-quality-mcp
_current_dir = Path(__file__).parent
_automation_mcp_dir = _current_dir / "mcp_servers" / "automation-quality-mcp"
_automation_mcp_server = _automation_mcp_dir / "mcpServer.js"
_automation_mcp_server_str = str(_automation_mcp_server.resolve())

client = MultiServerMCPClient(
    {
        "automation-quality": {
            "transport": "stdio",
            "command": "node",
            "args": [_automation_mcp_server_str],
            "env": {
                "NODE_ENV": "production",
                "OUTPUT_DIR": "./api-test-reports"
            }
        }
    }
)
tools = asyncio.run(client.get_tools())
agent = create_agent(model=model, tools=tools)
