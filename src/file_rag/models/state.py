"""
状态定义模块
定义工作流中使用的状态类型
"""
from typing import TypedDict
from langchain_core.messages import BaseMessage


class ConversationState(TypedDict, total=False):
    """对话状态定义（扩展版，支持测试用例生成）"""
    messages: list[BaseMessage]  # 消息历史
    file_type: str  # 文件类型: "image", "pdf", "text", "testcase_generation", "automated_test", "browser_operation"
    extracted_content: str  # 从PDF提取的文本内容
    # 测试用例生成相关字段（可选）
    test_requirement: str  # 测试需求
    test_cases: str  # 生成的测试用例
    test_review_result: str  # 评审结果: "通过" 或 "不通过"
    test_review_count: int  # 评审次数
    test_review_feedback: str  # 评审反馈意见
    waiting_for_user_review: bool  # 是否正在等待用户评审
    original_analysis: str  # 原始的图片/PDF分析结果（用于重新生成测试用例）
    used_multimodal: bool  # 是否使用了多模态模型（豆包）


class TestCaseGenerationState(TypedDict):
    """测试用例生成工作流状态（子工作流使用）"""
    messages: list[BaseMessage]  # 消息历史
    test_requirement: str  # 测试需求
    test_cases: str  # 生成的测试用例
    test_review_result: str  # 评审结果: "通过" 或 "不通过"
    test_review_count: int  # 评审次数
    test_review_feedback: str  # 评审反馈意见
    original_analysis: str  # 原始的图片/PDF分析结果（用于重新生成测试用例）
    used_multimodal: bool  # 是否使用了多模态模型（豆包）

