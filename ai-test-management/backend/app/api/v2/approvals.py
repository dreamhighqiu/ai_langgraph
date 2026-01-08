"""
审批管理 API

提供 Human-in-the-Loop 审批相关的接口
"""

from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.agents.human_in_the_loop_middleware import get_human_in_the_loop_middleware


router = APIRouter(prefix="/approvals")


class ApprovalRequest(BaseModel):
    """审批请求数据模型"""
    id: str = Field(..., description="审批请求 ID")
    tool: str = Field(..., description="工具名称")
    input: dict = Field(..., description="工具输入参数")
    timestamp: str = Field(..., description="创建时间")
    status: str = Field(..., description="状态：pending, approved, rejected")


class ApprovalFeedback(BaseModel):
    """审批反馈数据模型"""
    approved: bool = Field(..., description="是否批准")
    reason: Optional[str] = Field(None, description="拒绝原因")
    suggestions: Optional[List[str]] = Field(None, description="改进建议")
    feedback: Optional[dict] = Field(None, description="其他反馈信息")


class ApprovalResponse(BaseModel):
    """审批响应数据模型"""
    success: bool = Field(..., description="是否成功")
    message: str = Field(..., description="消息")
    approval: Optional[ApprovalRequest] = Field(None, description="审批请求信息")


class ApprovalListResponse(BaseModel):
    """审批列表响应"""
    success: bool = Field(..., description="是否成功")
    approvals: List[ApprovalRequest] = Field(..., description="审批请求列表")
    total: int = Field(..., description="总数")


@router.get(
    "",
    response_model=ApprovalListResponse,
    summary="获取审批请求列表",
    description="获取所有待审批的请求",
)
async def get_approvals(
    status_filter: Optional[str] = None,
) -> ApprovalListResponse:
    """
    获取审批请求列表
    
    Args:
        status_filter: 状态过滤（pending, approved, rejected）
    
    Returns:
        审批请求列表
    """
    middleware = get_human_in_the_loop_middleware()
    pending_approvals = middleware.get_pending_approvals()
    
    approvals = []
    for approval_id, approval_data in pending_approvals.items():
        if status_filter and approval_data["status"] != status_filter:
            continue
        
        approvals.append(ApprovalRequest(
            id=approval_id,
            tool=approval_data["tool"],
            input=approval_data["input"],
            timestamp=approval_data["timestamp"],
            status=approval_data["status"],
        ))
    
    return ApprovalListResponse(
        success=True,
        approvals=approvals,
        total=len(approvals),
    )


@router.get(
    "/{approval_id}",
    response_model=ApprovalResponse,
    summary="获取审批请求详情",
    description="获取指定审批请求的详细信息",
)
async def get_approval(
    approval_id: str,
) -> ApprovalResponse:
    """
    获取审批请求详情
    
    Args:
        approval_id: 审批请求 ID
    
    Returns:
        审批请求详情
    """
    middleware = get_human_in_the_loop_middleware()
    pending_approvals = middleware.get_pending_approvals()
    
    if approval_id not in pending_approvals:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"审批请求不存在：{approval_id}"
        )
    
    approval_data = pending_approvals[approval_id]
    
    return ApprovalResponse(
        success=True,
        message="获取审批请求成功",
        approval=ApprovalRequest(
            id=approval_id,
            tool=approval_data["tool"],
            input=approval_data["input"],
            timestamp=approval_data["timestamp"],
            status=approval_data["status"],
        ),
    )


@router.post(
    "/{approval_id}/submit",
    response_model=ApprovalResponse,
    summary="提交审批结果",
    description="批准或拒绝审批请求",
)
async def submit_approval(
    approval_id: str,
    feedback: ApprovalFeedback,
) -> ApprovalResponse:
    """
    提交审批结果
    
    Args:
        approval_id: 审批请求 ID
        feedback: 审批反馈
    
    Returns:
        审批结果
    """
    middleware = get_human_in_the_loop_middleware()
    
    if feedback.approved:
        # 批准
        success = middleware.approve_request(
            approval_id=approval_id,
            feedback=feedback.feedback,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"审批请求不存在：{approval_id}"
            )
        
        return ApprovalResponse(
            success=True,
            message="审批请求已批准",
        )
    else:
        # 拒绝
        success = middleware.reject_request(
            approval_id=approval_id,
            reason=feedback.reason,
            suggestions=feedback.suggestions,
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"审批请求不存在：{approval_id}"
            )
        
        return ApprovalResponse(
            success=True,
            message="审批请求已拒绝",
        )


@router.get(
    "/{approval_id}/status",
    summary="获取审批状态",
    description="获取指定审批请求的状态",
)
async def get_approval_status(
    approval_id: str,
) -> dict:
    """
    获取审批状态
    
    Args:
        approval_id: 审批请求 ID
    
    Returns:
        审批状态
    """
    middleware = get_human_in_the_loop_middleware()
    status_value = middleware.get_approval_status(approval_id)
    
    if status_value is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"审批请求不存在：{approval_id}"
        )
    
    return {
        "success": True,
        "approval_id": approval_id,
        "status": status_value,
    }

