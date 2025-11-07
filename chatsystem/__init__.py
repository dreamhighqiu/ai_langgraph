"""
多模态对话系统包
支持图片、PDF 和普通文本的智能对话
"""

import logging

# 获取日志记录器，但不配置根日志记录器
logger = logging.getLogger(__name__)

# 延迟导入，避免循环导入问题
def __getattr__(name):
    """延迟导入模块属性"""
    if name == "FileType":
        from chatsystem.types import FileType
        return FileType
    elif name == "ProcessorType":
        from chatsystem.types import ProcessorType
        return ProcessorType
    elif name == "ChatMessage":
        from chatsystem.types import ChatMessage
        return ChatMessage
    elif name == "ChatResult":
        from chatsystem.types import ChatResult
        return ChatResult
    elif name == "ProcessorConfig":
        from chatsystem.types import ProcessorConfig
        return ProcessorConfig
    elif name == "FileTypeDetector":
        from chatsystem.detectors import FileTypeDetector
        return FileTypeDetector
    elif name == "BaseProcessor":
        from chatsystem.processors import BaseProcessor
        return BaseProcessor
    elif name == "ImageProcessor":
        from chatsystem.processors import ImageProcessor
        return ImageProcessor
    elif name == "PDFProcessor":
        from chatsystem.processors import PDFProcessor
        return PDFProcessor
    elif name == "TextProcessor":
        from chatsystem.processors import TextProcessor
        return TextProcessor
    elif name == "ProcessorFactory":
        from chatsystem.processors import ProcessorFactory
        return ProcessorFactory
    elif name == "LLMFactory":
        from chatsystem.llm_factory import LLMFactory
        return LLMFactory
    elif name == "create_llm":
        from chatsystem.llm_factory import create_llm
        return create_llm
    elif name == "get_llm":
        from chatsystem.llm_factory import get_llm
        return get_llm
    elif name == "MultimodalChatSystem":
        from chatsystem.core import MultimodalChatSystem
        return MultimodalChatSystem
    elif name == "get_chat_system":
        from chatsystem.core import get_chat_system
        return get_chat_system
    elif name == "chat":
        from chatsystem.core import chat
        return chat
    elif name == "get_response":
        from chatsystem.core import get_response
        return get_response
    elif name == "agent_multimodal":
        from chatsystem.core import agent_multimodal
        return agent_multimodal
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

# 版本信息
__version__ = "1.0.0"
__author__ = "AI Agent"
__description__ = "多模态对话系统 - 支持图片、PDF 和普通文本的智能对话"

# 公共 API
__all__ = [
    # 类型
    "FileType",
    "ProcessorType",
    "ChatMessage",
    "ChatResult",
    "ProcessorConfig",

    # 检测器
    "FileTypeDetector",

    # 处理器
    "BaseProcessor",
    "ImageProcessor",
    "PDFProcessor",
    "TextProcessor",
    "ProcessorFactory",

    # LLM 工厂
    "LLMFactory",
    "create_llm",
    "get_llm",

    # 核心系统
    "MultimodalChatSystem",
    "get_chat_system",
    "chat",
    "get_response",

    # LangGraph 导出
    "agent_multimodal",
]


def get_version():
    """获取版本信息"""
    return __version__


def get_info():
    """获取包信息"""
    return {
        "name": "chatsystem",
        "version": __version__,
        "author": __author__,
        "description": __description__,
    }

