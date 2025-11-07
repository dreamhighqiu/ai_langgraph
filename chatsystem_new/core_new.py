"""
多模态对话系统核心模块 - 新架构

使用 StateGraph + 条件路由实现多模态对话
- 每种类型（图片、PDF、文本）使用独立的 Agent + 中间件
- 通过条件路由自动选择对应的处理节点
- 参照 image_agent.py 和 pdf_agent.py 的中间件模式
"""

import logging
from typing import Any, Dict, List

from langchain_core.messages import BaseMessage, HumanMessage
from langchain.agents import create_agent
from langgraph.graph import StateGraph, START, END

from chatsystem.types import FileType
from chatsystem.detectors import FileTypeDetector
from chatsystem.middleware import (
    image_chat_middleware,
    pdf_chat_middleware,
    text_chat_middleware,
)
from llm import create_llm

logger = logging.getLogger(__name__)


# ============================================================================
# Agent 创建
# ============================================================================

def _create_image_agent():
    """创建图片对话 Agent"""
    logger.info("创建图片对话 Agent...")
    llm = create_llm(model="gpt-4o")
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[image_chat_middleware],
    )
    logger.info("✅ 图片对话 Agent 创建成功")
    return agent


def _create_pdf_agent():
    """创建 PDF 对话 Agent"""
    logger.info("创建 PDF 对话 Agent...")
    llm = create_llm(model="gpt-4o")
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[pdf_chat_middleware],
    )
    logger.info("✅ PDF 对话 Agent 创建成功")
    return agent


def _create_text_agent():
    """创建文本对话 Agent"""
    logger.info("创建文本对话 Agent...")
    llm = create_llm(model="deepseek-chat")
    agent = create_agent(
        model=llm,
        tools=[],
        middleware=[text_chat_middleware],
    )
    logger.info("✅ 文本对话 Agent 创建成功")
    return agent


# ============================================================================
# 全局 Agent 实例
# ============================================================================

_image_agent = None
_pdf_agent = None
_text_agent = None


def _get_image_agent():
    """获取图片对话 Agent"""
    global _image_agent
    if _image_agent is None:
        _image_agent = _create_image_agent()
    return _image_agent


def _get_pdf_agent():
    """获取 PDF 对话 Agent"""
    global _pdf_agent
    if _pdf_agent is None:
        _pdf_agent = _create_pdf_agent()
    return _pdf_agent


def _get_text_agent():
    """获取文本对话 Agent"""
    global _text_agent
    if _text_agent is None:
        _text_agent = _create_text_agent()
    return _text_agent


# ============================================================================
# 节点函数
# ============================================================================

def detect_file_type(state: Dict[str, Any]) -> Dict[str, Any]:
    """检测文件类型节点"""
    logger.info("执行节点: 检测文件类型")
    
    messages = state.get("messages", [])
    if not messages:
        file_type = FileType.TEXT
    else:
        # 获取最后一条消息
        last_message = messages[-1]
        file_type = FileTypeDetector.detect_from_message(last_message)
    
    logger.info(f"✅ 检测到文件类型: {file_type.value}")
    state["file_type"] = file_type
    
    return state


def image_chat(state: Dict[str, Any]) -> Dict[str, Any]:
    """图片对话节点"""
    logger.info("执行节点: 图片对话")
    
    agent = _get_image_agent()
    messages = state.get("messages", [])
    
    result = agent.invoke({"messages": messages})
    state["response"] = result
    state["current_node"] = "image_chat"
    
    return state


def pdf_chat(state: Dict[str, Any]) -> Dict[str, Any]:
    """PDF 对话节点"""
    logger.info("执行节点: PDF 对话")
    
    agent = _get_pdf_agent()
    messages = state.get("messages", [])
    
    result = agent.invoke({"messages": messages})
    state["response"] = result
    state["current_node"] = "pdf_chat"
    
    return state


def text_chat(state: Dict[str, Any]) -> Dict[str, Any]:
    """文本对话节点"""
    logger.info("执行节点: 文本对话")
    
    agent = _get_text_agent()
    messages = state.get("messages", [])
    
    result = agent.invoke({"messages": messages})
    state["response"] = result
    state["current_node"] = "text_chat"
    
    return state


# ============================================================================
# 路由函数
# ============================================================================

def route_by_file_type(state: Dict[str, Any]) -> str:
    """根据文件类型路由"""
    file_type = state.get("file_type", FileType.TEXT)
    
    if file_type == FileType.IMAGE:
        logger.info("📸 路由到: 图片对话")
        return "image_chat"
    elif file_type == FileType.PDF:
        logger.info("📄 路由到: PDF 对话")
        return "pdf_chat"
    else:
        logger.info("📝 路由到: 文本对话")
        return "text_chat"


# ============================================================================
# 图构建
# ============================================================================

def _build_multimodal_graph():
    """构建多模态对话图"""
    logger.info("构建多模态对话图...")
    
    graph = StateGraph(dict)
    
    # 添加节点
    graph.add_node("detect_file_type", detect_file_type)
    graph.add_node("image_chat", image_chat)
    graph.add_node("pdf_chat", pdf_chat)
    graph.add_node("text_chat", text_chat)
    
    # 添加边
    graph.add_edge(START, "detect_file_type")
    
    # 条件路由
    graph.add_conditional_edges(
        "detect_file_type",
        route_by_file_type,
        {
            "image_chat": "image_chat",
            "pdf_chat": "pdf_chat",
            "text_chat": "text_chat",
        }
    )
    
    # 所有处理节点都连接到 END
    graph.add_edge("image_chat", END)
    graph.add_edge("pdf_chat", END)
    graph.add_edge("text_chat", END)
    
    logger.info("✅ 多模态对话图构建完成")
    return graph.compile()


# ============================================================================
# 全局系统实例
# ============================================================================

_compiled_graph = None


def _get_compiled_graph():
    """获取编译后的图"""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = _build_multimodal_graph()
    return _compiled_graph


# ============================================================================
# 公共 API
# ============================================================================

def chat(messages: List[BaseMessage]) -> Dict[str, Any]:
    """执行多模态对话"""
    logger.info(f"开始对话，消息数: {len(messages)}")
    
    graph = _get_compiled_graph()
    
    state = {
        "messages": messages,
        "file_type": FileType.UNKNOWN,
        "response": None,
        "current_node": None,
    }
    
    result = graph.invoke(state)
    
    logger.info(f"对话完成，使用节点: {result.get('current_node')}")
    
    return result


def get_response(messages: List[BaseMessage]) -> str:
    """获取对话响应"""
    result = chat(messages)
    return result.get("response", "")


# LangGraph API 导出
agent_multimodal_new = _get_compiled_graph()

