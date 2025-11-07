"""
多模态对话系统 Agent 工厂

使用 create_agent 和中间件来处理不同类型的对话
"""

import logging
from typing import Optional, List

from langchain.agents import create_agent
from langchain_core.runnables import RunnableConfig

from llm import create_llm
from chatsystem.middleware import detect_and_process_message

logger = logging.getLogger(__name__)


def create_multimodal_agent(
    model_name: str = "gpt-4o",
    tools: Optional[List] = None,
    config: Optional[RunnableConfig] = None
):
    """
    创建多模态对话 Agent
    
    关键逻辑:
    - 使用 create_agent 创建 Agent
    - 添加中间件来检测和处理不同类型的消息
    - 支持图片、PDF 和文本对话
    
    参数:
        model_name: LLM 模型名称
        tools: 可选的工具列表
        config: LangGraph API 配置对象
    
    返回:
        CompiledGraph: 编译后的 Agent 图
    """
    logger.info(f"创建多模态 Agent (模型: {model_name})")
    
    # 创建 LLM 实例
    llm = create_llm(model=model_name)
    
    # 如果没有提供工具，使用空列表
    if tools is None:
        tools = []
    
    # 创建 Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        middleware=[detect_and_process_message],
    )
    
    logger.info("✅ 多模态 Agent 创建成功")
    return agent


def create_image_agent(
    model_name: str = "gpt-4o",
    config: Optional[RunnableConfig] = None
):
    """
    创建图片处理 Agent
    
    参数:
        model_name: LLM 模型名称
        config: LangGraph API 配置对象
    
    返回:
        CompiledGraph: 编译后的 Agent 图
    """
    logger.info(f"创建图片处理 Agent (模型: {model_name})")
    
    llm = create_llm(model=model_name)
    
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[detect_and_process_message],
    )
    
    logger.info("✅ 图片处理 Agent 创建成功")
    return agent


def create_pdf_agent(
    model_name: str = "gpt-4o",
    config: Optional[RunnableConfig] = None
):
    """
    创建 PDF 处理 Agent
    
    参数:
        model_name: LLM 模型名称
        config: LangGraph API 配置对象
    
    返回:
        CompiledGraph: 编译后的 Agent 图
    """
    logger.info(f"创建 PDF 处理 Agent (模型: {model_name})")
    
    llm = create_llm(model=model_name)
    
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[detect_and_process_message],
    )
    
    logger.info("✅ PDF 处理 Agent 创建成功")
    return agent


def create_text_agent(
    model_name: str = "gpt-4o",
    config: Optional[RunnableConfig] = None
):
    """
    创建文本处理 Agent
    
    参数:
        model_name: LLM 模型名称
        config: LangGraph API 配置对象
    
    返回:
        CompiledGraph: 编译后的 Agent 图
    """
    logger.info(f"创建文本处理 Agent (模型: {model_name})")
    
    llm = create_llm(model=model_name)
    
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[detect_and_process_message],
    )
    
    logger.info("✅ 文本处理 Agent 创建成功")
    return agent

