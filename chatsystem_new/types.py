"""
多模态对话系统类型定义
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


class FileType(str, Enum):
    """文件类型枚举"""
    IMAGE = "image"      # 图片文件
    PDF = "pdf"          # PDF 文件
    TEXT = "text"        # 普通文本
    UNKNOWN = "unknown"  # 未知类型


class ProcessorType(str, Enum):
    """处理器类型枚举"""
    IMAGE = "image"      # 图片处理器
    PDF = "pdf"          # PDF 处理器
    TEXT = "text"        # 文本处理器


@dataclass
class ChatMessage:
    """对话消息"""
    role: str           # 角色: user, assistant, system
    content: str        # 消息内容
    metadata: Optional[Dict[str, Any]] = None  # 元数据


@dataclass
class ChatResult:
    """对话结果"""
    response: str                    # 响应内容
    file_type: FileType             # 检测到的文件类型
    processor_type: ProcessorType    # 使用的处理器类型
    messages: List[ChatMessage]      # 消息列表
    metadata: Optional[Dict[str, Any]] = None  # 元数据


@dataclass
class ProcessorConfig:
    """处理器配置"""
    model: str                       # 模型名称
    temperature: float = 0.7         # 温度
    max_tokens: int = 2000           # 最大 token 数
    timeout: int = 60                # 超时时间（秒）
    retry_count: int = 3             # 重试次数
    metadata: Optional[Dict[str, Any]] = None  # 元数据

