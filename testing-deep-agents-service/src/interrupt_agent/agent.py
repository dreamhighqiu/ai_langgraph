"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
# type: ignore  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Wm0xcldRPT06NWQ4NzNiMTQ=

from langchain.tools import tool
from deepagents import create_deep_agent
from langchain_deepseek import ChatDeepSeek
from langgraph.checkpoint.memory import MemorySaver

@tool
def delete_file(path: str) -> str:
    """Delete a file from the filesystem."""
    return f"Deleted {path}"

@tool
def read_file(path: str) -> str:
    """Read a file from the filesystem."""
    return f"Contents of {path}"

@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email."""
    return f"Sent email to {to}"

# Checkpointer is REQUIRED for human-in-the-loop
# checkpointer = MemorySaver()
os.environ["DEEPSEEK_API_KEY"] = "sk-ab8dda459d2a4203b71c6aa2065b411a"
deepseek = ChatDeepSeek(model="deepseek-chat")
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Wm0xcldRPT06NWQ4NzNiMTQ=

agent = create_deep_agent(
    model=deepseek,
    tools=[delete_file, read_file, send_email],
    interrupt_on={
        "delete_file": True,  # Default: approve, edit, reject
        "read_file": False,   # No interrupts needed
        "send_email": {"allowed_decisions": ["approve", "reject"]},  # No editing
    },
    # checkpointer=checkpointer  # Required!
)