

import os

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware, InterruptOnConfig
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVRnMFl3PT06ZjRkOGI2Mjc=

# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TVRnMFl3PT06ZjRkOGI2Mjc=

def read_email_tool(email_id: str) -> str:
    """Mock function to read an email by its ID."""
    return f"Email content for ID: {email_id}"

def send_email_tool(recipient: str, subject: str, body: str) -> str:
    """Mock function to send an email."""
    return f"Email sent to {recipient} with subject '{subject}'"
os.environ["DEEPSEEK_API_KEY"] = "sk-0292e5a35e064f6f86169a20e39f0749"
model = init_chat_model("deepseek:deepseek-chat")
agent = create_agent(
    model=model,
    tools=[read_email_tool, send_email_tool],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"send_email_tool": InterruptOnConfig(
                allowed_decisions=["approve", "edit", "reject"],
            )}
        )
    ],
)

# agent = create_agent(
#     model=model,
#     tools=[read_email_tool, send_email_tool],
#     # checkpointer=InMemorySaver(),
#     middleware=[
#         HumanInTheLoopMiddleware(
#             interrupt_on={
#                 "send_email_tool": {
#                     "allowed_decisions": ["approve", "edit", "reject"],
#                 },
#                 "read_email_tool": False,
#             }
#         ),
#     ],
# )