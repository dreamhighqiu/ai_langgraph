"""
状态定义模块
定义工作流中使用的状态类型
"""
from typing import TypedDict
from langchain_core.messages import BaseMessage


class ConversationState(TypedDict, total=False):
    """
    通用对话状态定义

    用于主工作流的通用状态，保持简洁
    特定功能的状态应该在各自的模块中定义
    """
    messages: list[BaseMessage]  # 消息历史
    file_type: str  # 文件类型: "image", "pdf", "text", "testcase_generation", "automated_test", "browser_operation"
    extracted_content: str  # 从PDF/图片提取的文本内容

