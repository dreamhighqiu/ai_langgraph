"""
Human-in-the-Loop 中间件

实现测试用例评审的人工参与机制
"""

import logging
from typing import Callable, Optional, Dict, Any
from datetime import datetime

from langchain.agents.middleware import AgentMiddleware, ModelRequest, ModelResponse
from langchain.messages import HumanMessage

logger = logging.getLogger(__name__)


class HumanInTheLoopMiddleware(AgentMiddleware):
    """
    Human-in-the-Loop 中间件
    
    功能：
    1. 拦截需要人工审批的工具调用
    2. 产生中断，等待用户反馈
    3. 将用户反馈注入到后续的执行流程中
    """
    
    def __init__(
        self,
        tools_requiring_approval: Optional[list[str]] = None,
        approval_callback: Optional[Callable] = None,
    ):
        """
        初始化 Human-in-the-Loop 中间件
        
        Args:
            tools_requiring_approval: 需要人工审批的工具名称列表
            approval_callback: 审批回调函数，用于处理审批请求
        """
        self.tools_requiring_approval = tools_requiring_approval or ["review_test_case_tool"]
        self.approval_callback = approval_callback
        self.pending_approvals: Dict[str, Any] = {}
        
        logger.info(
            f"Human-in-the-Loop 中间件初始化完成，监控工具：{self.tools_requiring_approval}"
        )
    
    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        """
        异步拦截模型调用，处理 Human-in-the-Loop 逻辑
        
        Args:
            request: 模型请求对象
            handler: 原始处理函数
        
        Returns:
            ModelResponse: 模型响应
        """
        # 执行原始处理
        response = await handler(request)
        
        # 检查响应中是否有工具调用
        if not hasattr(response, "tool_calls") or not response.tool_calls:
            return response
        
        # 检查是否有需要审批的工具调用
        for tool_call in response.tool_calls:
            tool_name = tool_call.get("name", "")
            
            if tool_name in self.tools_requiring_approval:
                logger.info(f"检测到需要人工审批的工具调用：{tool_name}")
                
                # 获取工具输入
                tool_input = tool_call.get("args", {})
                
                # 检查工具输出是否包含 requires_human_input 标志
                if isinstance(tool_input, dict) and tool_input.get("requires_human_input"):
                    # 产生中断
                    await self._handle_approval_request(tool_name, tool_input)
        
        return response
    
    async def _handle_approval_request(
        self,
        tool_name: str,
        tool_input: Dict[str, Any]
    ) -> None:
        """
        处理审批请求
        
        Args:
            tool_name: 工具名称
            tool_input: 工具输入参数
        """
        approval_id = f"{tool_name}_{datetime.now().timestamp()}"
        
        approval_request = {
            "id": approval_id,
            "tool": tool_name,
            "input": tool_input,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
        }
        
        # 保存待审批请求
        self.pending_approvals[approval_id] = approval_request
        
        logger.info(f"创建审批请求：{approval_id}")
        
        # 如果配置了回调函数，调用它
        if self.approval_callback:
            try:
                await self.approval_callback(approval_request)
            except Exception as e:
                logger.error(f"审批回调执行失败：{e}", exc_info=True)
    
    def get_pending_approvals(self) -> Dict[str, Any]:
        """获取待审批的请求列表"""
        return self.pending_approvals
    
    def approve_request(self, approval_id: str, feedback: Optional[Dict[str, Any]] = None) -> bool:
        """
        批准审批请求
        
        Args:
            approval_id: 审批请求 ID
            feedback: 用户反馈
        
        Returns:
            bool: 是否成功批准
        """
        if approval_id not in self.pending_approvals:
            logger.warning(f"审批请求不存在：{approval_id}")
            return False
        
        self.pending_approvals[approval_id]["status"] = "approved"
        self.pending_approvals[approval_id]["feedback"] = feedback
        self.pending_approvals[approval_id]["approved_at"] = datetime.now().isoformat()
        
        logger.info(f"审批请求已批准：{approval_id}")
        return True
    
    def reject_request(
        self,
        approval_id: str,
        reason: Optional[str] = None,
        suggestions: Optional[list[str]] = None
    ) -> bool:
        """
        拒绝审批请求
        
        Args:
            approval_id: 审批请求 ID
            reason: 拒绝原因
            suggestions: 改进建议
        
        Returns:
            bool: 是否成功拒绝
        """
        if approval_id not in self.pending_approvals:
            logger.warning(f"审批请求不存在：{approval_id}")
            return False
        
        self.pending_approvals[approval_id]["status"] = "rejected"
        self.pending_approvals[approval_id]["reason"] = reason
        self.pending_approvals[approval_id]["suggestions"] = suggestions or []
        self.pending_approvals[approval_id]["rejected_at"] = datetime.now().isoformat()
        
        logger.info(f"审批请求已拒绝：{approval_id}，原因：{reason}")
        return True
    
    def get_approval_status(self, approval_id: str) -> Optional[str]:
        """
        获取审批请求状态
        
        Args:
            approval_id: 审批请求 ID
        
        Returns:
            str: 状态（pending, approved, rejected）
        """
        if approval_id not in self.pending_approvals:
            return None
        
        return self.pending_approvals[approval_id]["status"]


# ============ 全局中间件实例 ============

# 用于在应用中共享的全局中间件实例
_human_in_the_loop_middleware: Optional[HumanInTheLoopMiddleware] = None


def get_human_in_the_loop_middleware() -> HumanInTheLoopMiddleware:
    """获取全局 Human-in-the-Loop 中间件实例"""
    global _human_in_the_loop_middleware
    
    if _human_in_the_loop_middleware is None:
        _human_in_the_loop_middleware = HumanInTheLoopMiddleware()
    
    return _human_in_the_loop_middleware


def set_human_in_the_loop_middleware(middleware: HumanInTheLoopMiddleware) -> None:
    """设置全局 Human-in-the-Loop 中间件实例"""
    global _human_in_the_loop_middleware
    _human_in_the_loop_middleware = middleware

