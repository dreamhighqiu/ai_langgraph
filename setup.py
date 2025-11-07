"""
AI LangGraph 项目安装配置
"""

from setuptools import setup, find_packages

setup(
    name="ai_langgraph",
    version="1.0.0",
    description="AI LangGraph 多模态对话系统",
    author="AI Agent",
    packages=find_packages(exclude=["debug", "docs", "example", "graphs_examples", "jmeter", "testing-agent-chat-ui"]),
    python_requires=">=3.11",
    install_requires=[
        "langchain-core>=0.1.0",
        "langchain-openai>=0.0.5",
        "langgraph>=0.0.20",
        "pymupdf4llm>=0.0.1",
        "pymupdf>=1.23.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
        ],
    },
)

