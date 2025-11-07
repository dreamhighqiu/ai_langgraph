"""
多模态对话系统中间件模块

为每种对话类型提供专门的中间件
- 图片对话中间件: 处理图片内容
- PDF 对话中间件: 处理 PDF 文件
- 文本对话中间件: 处理普通文本
"""

import logging
import base64
import tempfile
import os
from typing import Any, Dict, List

from langchain.agents import AgentState
from langchain.agents.middleware import before_model
from langchain_core.messages import HumanMessage
from langchain_pymupdf4llm import PyMuPDF4LLMLoader
import fitz

logger = logging.getLogger(__name__)


def detect_file_type_before_model(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    在模型调用前检测文件类型的中间件
    
    关键逻辑:
    - 获取最后一条消息
    - 检测文件类型（图片、PDF 或文本）
    - 将文件类型存储到 state 中
    - 根据文件类型选择合适的处理节点
    
    参数:
        state: 包含消息列表的状态字典
    
    返回:
        更新后的 state 字典
    """
    logger.info("=" * 60)
    logger.info("中间件执行: 检测文件类型")
    logger.info("=" * 60)
    
    messages = state.get("messages", [])
    
    if not messages:
        logger.warning("没有消息，默认为文本模式")
        file_type = FileType.TEXT
        current_node = "process_text"
    else:
        # 获取最后一条消息
        last_message = messages[-1]
        logger.debug(f"获取最后一条消息: {type(last_message).__name__}")
        
        # 检测文件类型
        file_type = FileTypeDetector.detect_from_message(last_message)
        logger.info(f"✅ 检测到文件类型: {file_type.value}")
        
        # 根据文件类型确定处理节点
        if file_type == FileType.IMAGE:
            current_node = "process_image"
            logger.info("📸 将路由到图片处理节点")
        elif file_type == FileType.PDF:
            current_node = "process_pdf"
            logger.info("📄 将路由到 PDF 处理节点")
        else:
            current_node = "process_text"
            logger.info("📝 将路由到文本处理节点")
    
    # 将检测结果存储到 state 中
    state["file_type"] = file_type
    state["current_mode"] = file_type.value
    state["current_node"] = current_node
    
    logger.info(f"当前对话模式: {file_type.value}")
    logger.info(f"将路由到节点: {current_node}")
    logger.info("=" * 60)
    
    return state


def get_current_chat_type(state: Dict[str, Any]) -> tuple:
    """
    获取当前聊天的类型

    关键逻辑:
    - 始终获取最后一条消息
    - 检测最后一条消息的文件类型
    - 这样可以在同一个聊天过程中支持模式切换

    参数:
        state: 包含消息列表的状态字典

    返回:
        (file_type, current_node): 文件类型和对应的处理节点
    """
    messages = state.get("messages", [])

    if not messages:
        logger.warning("没有消息，默认为文本模式")
        return FileType.TEXT, "process_text"

    # 获取最后一条消息
    last_message = messages[-1]
    logger.debug(f"获取最后一条消息: {type(last_message).__name__}")

    # 检测文件类型
    file_type = FileTypeDetector.detect_from_message(last_message)
    logger.info(f"检测到文件类型: {file_type.value}")

    # 根据文件类型确定处理节点
    if file_type == FileType.IMAGE:
        current_node = "process_image"
    elif file_type == FileType.PDF:
        current_node = "process_pdf"
    else:
        current_node = "process_text"

    logger.info(f"当前对话模式: {file_type.value}")
    logger.info(f"将路由到节点: {current_node}")

    return file_type, current_node


def detect_and_process_message(state: Dict[str, Any]) -> None:
    """
    检测消息类型并处理对应的内容

    关键逻辑:
    - 获取最后一条消息
    - 检测文件类型
    - 根据类型处理消息内容
    - 添加错误处理和日志

    参数:
        state: Agent 状态

    返回:
        None
    """
    import time

    start_time = time.time()

    logger.info("=" * 60)
    logger.info("中间件执行: 检测并处理消息类型")
    logger.info("=" * 60)

    try:
        messages = state.get("messages", [])

        if not messages:
            logger.warning("⚠️ 没有消息")
            state["response"] = "没有消息"
            return None

        # 获取最后一条消息
        last_message = messages[-1]
        logger.debug(f"获取最后一条消息: {type(last_message).__name__}")

        # 检测文件类型
        file_type = FileTypeDetector.detect_from_message(last_message)
        logger.info(f"✅ 检测到文件类型: {file_type.value}")

        # 根据文件类型处理
        if file_type == FileType.IMAGE:
            logger.info("📸 处理图片消息")
            _process_image_message(state, last_message)
        elif file_type == FileType.PDF:
            logger.info("📄 处理 PDF 消息")
            _process_pdf_message(state, last_message)
        else:
            logger.info("📝 处理文本消息")
            _process_text_message(state, last_message)

        elapsed_time = time.time() - start_time
        logger.info(f"✅ 消息处理完成，耗时: {elapsed_time:.2f}s")
        logger.info("=" * 60)

        return None

    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(f"❌ 消息处理失败 ({elapsed_time:.2f}s): {e}")
        logger.error(f"错误详情: {type(e).__name__}")
        state["response"] = f"处理失败: {str(e)}"
        logger.info("=" * 60)
        return None


def _process_image_message(state: Dict[str, Any], message: HumanMessage) -> None:
    """
    处理图片消息

    使用 ImageProcessor 处理图片内容
    """
    try:
        from chatsystem.processors import ProcessorFactory
        from chatsystem.types import FileType

        logger.info("📸 处理图片消息...")

        processor = ProcessorFactory.create_processor(FileType.IMAGE)
        response = processor.process([message])

        state["response"] = response
        state["processor_type"] = "image"

        logger.info(f"✅ 图片处理完成")

    except Exception as e:
        logger.error(f"❌ 图片处理失败: {e}")
        state["response"] = f"图片处理失败: {str(e)}"


def _process_pdf_message(state: Dict[str, Any], message: HumanMessage) -> None:
    """
    处理 PDF 消息

    使用 PDFProcessor 处理 PDF 内容
    """
    try:
        from chatsystem.processors import ProcessorFactory
        from chatsystem.types import FileType

        logger.info("📄 处理 PDF 消息...")

        processor = ProcessorFactory.create_processor(FileType.PDF)
        response = processor.process([message])

        state["response"] = response
        state["processor_type"] = "pdf"

        logger.info(f"✅ PDF 处理完成")

    except Exception as e:
        logger.error(f"❌ PDF 处理失败: {e}")
        state["response"] = f"PDF 处理失败: {str(e)}"


def _process_text_message(state: Dict[str, Any], message: HumanMessage) -> None:
    """
    处理文本消息

    使用 TextProcessor 处理文本内容
    """
    try:
        from chatsystem.processors import ProcessorFactory
        from chatsystem.types import FileType

        logger.info("📝 处理文本消息...")

        processor = ProcessorFactory.create_processor(FileType.TEXT)
        response = processor.process([message])

        state["response"] = response
        state["processor_type"] = "text"

        logger.info(f"✅ 文本处理完成")

    except Exception as e:
        logger.error(f"❌ 文本处理失败: {e}")
        state["response"] = f"文本处理失败: {str(e)}"

