"""
缺陷报告视图对象
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class BugReportVO(BaseModel):
    """缺陷报告VO - 用于创建和更新"""
    project_id: int = Field(..., description="项目ID")
    bug_title: str = Field(..., max_length=200, description="缺陷标题")
    bug_description: str = Field(..., description="缺陷描述")
    severity: str = Field(..., description="严重程度")
    priority: str = Field(..., description="优先级")
    bug_type: str = Field(..., description="缺陷类型")
    status: Optional[str] = Field("open", description="状态")
    environment: Optional[str] = Field(None, description="环境信息")
    steps_to_reproduce: Optional[str] = Field(None, description="复现步骤")
    expected_behavior: Optional[str] = Field(None, description="预期行为")
    actual_behavior: Optional[str] = Field(None, description="实际行为")
    attachments: Optional[str] = Field(None, description="附件")
    assigned_to: Optional[int] = Field(None, description="分配给")


class BugReportQueryVO(BaseModel):
    """查询缺陷报告请求"""
    project_id: Optional[int] = Field(None, description="项目ID")
    bug_title: Optional[str] = Field(None, description="缺陷标题(模糊查询)")
    severity: Optional[str] = Field(None, description="严重程度")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    bug_type: Optional[str] = Field(None, description="缺陷类型")
    assigned_to: Optional[int] = Field(None, description="分配给")
    reporter: Optional[int] = Field(None, description="报告人")
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class BugReportGenerateVO(BaseModel):
    """AI生成缺陷报告VO"""
    project_id: int = Field(..., description="项目ID")
    issue_summary: str = Field(..., description="问题摘要")
    issue_description: str = Field(..., description="问题描述")
    environment: Optional[str] = Field(None, description="环境信息")
    severity: str = Field("medium", description="严重程度")
    thread_id: Optional[str] = Field(None, description="会话ID")
    auto_save: bool = Field(False, description="是否自动保存")

