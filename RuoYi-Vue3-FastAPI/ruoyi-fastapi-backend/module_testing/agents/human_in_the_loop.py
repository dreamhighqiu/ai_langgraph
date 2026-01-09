"""
Human-in-the-Loop 中间件

参照 ai-test-management 项目实现
支持测试用例评审、工具审批等人工干预场景

关键功能：
1. 测试用例评审中断
2. 工具调用审批
3. 中断状态管理
"""
import json
from typing import Any, Dict, Optional, List, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from langgraph.checkpoint.base import BaseCheckpointSaver
from utils.log_util import logger


class InterruptType(str, Enum):
    """中断类型"""
    TEST_CASE_REVIEW = "test_case_review"  # 测试用例评审
    TOOL_APPROVAL = "tool_approval"  # 工具调用审批
    HUMAN_INPUT = "human_input"  # 需要人工输入
    CONFIRMATION = "confirmation"  # 确认操作


@dataclass
class InterruptRequest:
    """中断请求"""
    interrupt_id: str
    interrupt_type: InterruptType
    title: str
    description: str
    data: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, rejected, timeout
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "interrupt_id": self.interrupt_id,
            "interrupt_type": self.interrupt_type.value,
            "title": self.title,
            "description": self.description,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }


@dataclass
class InterruptResponse:
    """中断响应"""
    interrupt_id: str
    approved: bool
    feedback: Optional[str] = None
    modifications: Optional[Dict[str, Any]] = None
    responded_at: datetime = field(default_factory=datetime.now)


class HumanInTheLoopManager:
    """Human-in-the-Loop 管理器"""
    
    def __init__(self):
        """初始化管理器"""
        # 存储待处理的中断请求
        self._pending_interrupts: Dict[str, InterruptRequest] = {}
        # 中断回调函数
        self._interrupt_callbacks: List[Callable] = []
    
    def create_review_interrupt(
        self,
        test_case_content: str,
        review_aspects: List[str],
        thread_id: str
    ) -> InterruptRequest:
        """
        创建测试用例评审中断
        
        Args:
            test_case_content: 测试用例内容（JSON 字符串）
            review_aspects: 评审方面
            thread_id: 对话线程 ID
            
        Returns:
            InterruptRequest: 中断请求
        """
        import uuid
        
        interrupt_id = f"review_{uuid.uuid4().hex[:8]}"
        
        # 解析测试用例内容
        try:
            if isinstance(test_case_content, str):
                test_case_data = json.loads(test_case_content)
            else:
                test_case_data = test_case_content
            test_case_name = test_case_data.get("name", "未命名测试用例")
        except:
            test_case_name = "测试用例"
            test_case_data = {"content": test_case_content}
        
        interrupt = InterruptRequest(
            interrupt_id=interrupt_id,
            interrupt_type=InterruptType.TEST_CASE_REVIEW,
            title=f"请评审测试用例: {test_case_name}",
            description="AI 已生成测试用例，请进行评审确认",
            data={
                "thread_id": thread_id,
                "test_case": test_case_data,
                "review_aspects": review_aspects,
                "aspect_descriptions": {
                    "completeness": "测试用例是否覆盖所有必要场景（正常流程、异常流程、边界条件）",
                    "accuracy": "测试步骤和预期结果是否准确、清晰",
                    "executability": "测试用例是否可以实际执行，前置条件是否完整",
                    "clarity": "测试用例描述是否清晰易懂，术语使用是否准确",
                }
            }
        )
        
        self._pending_interrupts[interrupt_id] = interrupt
        logger.info(f"创建测试用例评审中断: {interrupt_id}")
        
        return interrupt
    
    def create_tool_approval_interrupt(
        self,
        tool_name: str,
        tool_args: Dict[str, Any],
        thread_id: str,
        description: Optional[str] = None
    ) -> InterruptRequest:
        """
        创建工具调用审批中断
        
        Args:
            tool_name: 工具名称
            tool_args: 工具参数
            thread_id: 对话线程 ID
            description: 描述
            
        Returns:
            InterruptRequest: 中断请求
        """
        import uuid
        
        interrupt_id = f"tool_{uuid.uuid4().hex[:8]}"
        
        tool_display_names = {
            "create_test_case_tool": "创建测试用例",
            "update_test_case_tool": "更新测试用例",
            "batch_create_test_cases_tool": "批量创建测试用例",
            "save_requirement_analysis_tool": "保存需求分析",
            "save_defect_analysis_tool": "保存缺陷分析",
        }
        
        display_name = tool_display_names.get(tool_name, tool_name)
        
        interrupt = InterruptRequest(
            interrupt_id=interrupt_id,
            interrupt_type=InterruptType.TOOL_APPROVAL,
            title=f"请确认执行: {display_name}",
            description=description or f"AI 请求执行 {display_name} 操作，请确认是否允许",
            data={
                "thread_id": thread_id,
                "tool_name": tool_name,
                "tool_args": tool_args,
                "display_name": display_name
            }
        )
        
        self._pending_interrupts[interrupt_id] = interrupt
        logger.info(f"创建工具审批中断: {interrupt_id}, 工具: {tool_name}")
        
        return interrupt
    
    def resolve_interrupt(
        self,
        interrupt_id: str,
        approved: bool,
        feedback: Optional[str] = None,
        modifications: Optional[Dict[str, Any]] = None
    ) -> InterruptResponse:
        """
        解决中断
        
        Args:
            interrupt_id: 中断 ID
            approved: 是否批准
            feedback: 反馈意见
            modifications: 修改内容
            
        Returns:
            InterruptResponse: 中断响应
        """
        if interrupt_id not in self._pending_interrupts:
            raise ValueError(f"中断请求不存在: {interrupt_id}")
        
        interrupt = self._pending_interrupts[interrupt_id]
        interrupt.status = "approved" if approved else "rejected"
        
        response = InterruptResponse(
            interrupt_id=interrupt_id,
            approved=approved,
            feedback=feedback,
            modifications=modifications
        )
        
        # 从待处理列表移除
        del self._pending_interrupts[interrupt_id]
        
        logger.info(f"中断已解决: {interrupt_id}, 状态: {interrupt.status}")
        
        return response
    
    def get_pending_interrupt(self, interrupt_id: str) -> Optional[InterruptRequest]:
        """获取待处理的中断"""
        return self._pending_interrupts.get(interrupt_id)
    
    def get_all_pending_interrupts(self, thread_id: Optional[str] = None) -> List[InterruptRequest]:
        """获取所有待处理的中断"""
        interrupts = list(self._pending_interrupts.values())
        
        if thread_id:
            interrupts = [
                i for i in interrupts 
                if i.data.get("thread_id") == thread_id
            ]
        
        return interrupts
    
    def has_pending_interrupts(self, thread_id: Optional[str] = None) -> bool:
        """检查是否有待处理的中断"""
        return len(self.get_all_pending_interrupts(thread_id)) > 0


# 全局实例
_hitl_manager: Optional[HumanInTheLoopManager] = None


def get_hitl_manager() -> HumanInTheLoopManager:
    """获取 Human-in-the-Loop 管理器单例"""
    global _hitl_manager
    if _hitl_manager is None:
        _hitl_manager = HumanInTheLoopManager()
    return _hitl_manager


# ============ 工具函数 ============

async def review_test_case_tool(
    test_case_content: str,
    review_aspects: Optional[List[str]] = None,
    thread_id: str = ""
) -> Dict[str, Any]:
    """
    测试用例评审工具（需要人工参与）
    
    该工具用于对生成的测试用例进行评审，会产生中断点让用户参与评审。
    
    Args:
        test_case_content: 待评审的测试用例内容（JSON 格式字符串）
        review_aspects: 需要评审的方面
        thread_id: 对话线程 ID
        
    Returns:
        dict: 包含评审请求的字典
    """
    review_aspects = review_aspects or ["completeness", "accuracy", "executability", "clarity"]
    
    manager = get_hitl_manager()
    interrupt = manager.create_review_interrupt(
        test_case_content=test_case_content,
        review_aspects=review_aspects,
        thread_id=thread_id
    )
    
    return {
        "success": True,
        "requires_human_input": True,
        "interrupt": interrupt.to_dict(),
        "message": f"测试用例已提交评审，等待用户反馈...",
        "pending": True
    }

