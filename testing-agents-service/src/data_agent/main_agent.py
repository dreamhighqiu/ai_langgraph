"""Supervisor Agent - Multi-agent orchestration using tool calling pattern.

This supervisor coordinates two specialized sub-agents:
1. chat_rag_agent: For answering questions based on RAG knowledge base
2. data_import_agent: For crawling and importing API documentation into RAG
"""


import asyncio
import os
from langchain.agents import create_agent
from langchain.tools import tool
from dotenv import load_dotenv
from config.llm_config import get_llm
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0c1NmFBPT06YmUwMTc5YTk=

from data_agent.chat_rag_agent import agent as rag_agent
from data_agent.data_import_agent import agent as import_agent

# Initialize LLM for supervisor（使用 DeepSeek）
load_dotenv()
llm = get_llm(provider="deepseek", model_name="deepseek-chat")
async def test():
    pass

@tool(
    "chat_rag_agent",
    description="""Use this tool to answer questions based on the RAG knowledge base.

This agent can:
- Answer questions about API documentation stored in the knowledge base
- Retrieve relevant information from previously imported documents
- Provide explanations based on indexed content

Use this when the user asks questions that require searching the knowledge base."""
)
def chat_rag_tool(query: str) -> str:
    """Query the RAG agent to answer questions from the knowledge base."""
    result = asyncio.run(rag_agent.ainvoke({
        "messages": [{"role": "user", "content": query}]
    }))
    # Return the final message content
    return result["messages"][-1].content


@tool(
    "data_import_agent",
    description="""Use this tool to crawl and import API documentation into the RAG knowledge base.

This agent can:
- Extract URLs from user messages
- Crawl web pages to fetch API documentation
- Filter and extract API-related content
- Insert documents into the RAG knowledge base

Use this when the user wants to:
- Import new API documentation from a URL
- Crawl and index a website
- Add new content to the knowledge base"""
)
def data_import_tool(query: str) -> str:
    """Import data from URLs into the RAG knowledge base."""
    result = asyncio.run(import_agent.ainvoke({
        "messages": [{"role": "user", "content": query}]
    }))
    # Return the final message content
    if result.get("messages"):
        return result["messages"][-1].content
    # If no messages, return a summary of the operation
    crawled = len(result.get("crawled_data", []))
    filtered = len(result.get("filtered_data", []))
    return f"Data import completed. Crawled: {crawled} URLs, Filtered: {filtered} documents."
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0c1NmFBPT06YmUwMTc5YTk=


# Create supervisor agent with the sub-agent tools
SUPERVISOR_PROMPT = """You are a helpful assistant that coordinates specialized agents.

You have access to two specialized agents:
1. chat_rag_agent: For answering questions from the RAG knowledge base
2. data_import_agent: For importing/crawling API documentation into the knowledge base

Based on the user's request, decide which agent to use:
- If the user asks a question about API documentation or wants information, use chat_rag_agent
- If the user wants to import, crawl, or add new documentation, use data_import_agent

Always use the appropriate agent to handle the user's request."""

supervisor_agent = create_agent(
    model=llm,
    tools=[chat_rag_tool, data_import_tool],
    system_prompt=SUPERVISOR_PROMPT
)
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0c1NmFBPT06YmUwMTc5YTk=

# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2U0c1NmFBPT06YmUwMTc5YTk=

# For convenience, expose the supervisor as the main agent
agent = supervisor_agent


if __name__ == "__main__":
    # Test the supervisor agent
    result = agent.invoke({
        "messages": [{"role": "user", "content": "请帮我导入 https://example.com/api-docs 的文档"}]
    })
    print(result)
    