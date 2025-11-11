"""
测试用例生成工作流状态定义

独立的状态类，用于测试用例生成工作流
"""
from typing import TypedDict
from langchain_core.messages import BaseMessage


class TestCaseState(TypedDict, total=False):
    """
    测试用例生成工作流状态定义
    
    用于独立的测试用例生成工作流，包含所有测试用例相关的字段
    """
    # 基础字段
    messages: list[BaseMessage]  # 消息历史
    file_type: str  # 文件类型: "image", "pdf", "text"
    extracted_content: str  # 从PDF/图片提取的内容
    
    # 测试需求字段
    test_requirement: str  # 测试需求描述
    
    # 测试用例生成字段
    test_cases: str  # 生成的测试用例（字符串格式，JSON）
    test_cases_list: list  # 生成的测试用例（列表格式）
    
    # 评审相关字段
    test_review_count: int  # 评审次数
    test_review_result: str  # 评审结果: "通过" 或 "不通过"
    test_review_feedback: str  # 评审反馈意见
    
    # AI 自动评审字段
    review_passed: bool  # 评审是否通过
    review_score: int  # 评审得分 (0-100)
    review_summary: str  # 评审总体评价
    review_issues: list  # 评审发现的问题
    review_suggestions: list  # 评审改进建议
    review_feedback: str  # 评审反馈信息
    
    # 其他字段
    original_analysis: str  # 原始的图片/PDF分析结果（用于重新生成测试用例）
    used_multimodal: bool  # 是否使用了多模态模型
    file_path: str  # 保存的文件路径

