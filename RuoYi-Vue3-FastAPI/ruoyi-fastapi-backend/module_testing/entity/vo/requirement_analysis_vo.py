"""
需求分析视图对象
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class RequirementAnalysisVO(BaseModel):
    """需求分析VO - 用于创建和更新"""
    project_id: int = Field(..., description="项目ID")
    requirement_name: str = Field(..., max_length=200, description="需求名称")
    requirement_type: str = Field(..., description="需求类型")
    priority: str = Field(..., description="优先级")
    status: Optional[str] = Field("draft", description="状态")
    module: Optional[str] = Field(None, description="所属模块")
    description: Optional[str] = Field(None, description="需求描述")
    acceptance_criteria: Optional[str] = Field(None, description="验收标准")
    functional_requirements: Optional[str] = Field(None, description="功能需求")
    non_functional_requirements: Optional[str] = Field(None, description="非功能需求")
    business_rules: Optional[str] = Field(None, description="业务规则")
    dependencies: Optional[str] = Field(None, description="依赖关系")
    stakeholders: Optional[str] = Field(None, description="相关干系人")


class RequirementAnalysisQueryVO(BaseModel):
    """查询需求分析请求"""
    project_id: Optional[int] = Field(None, description="项目ID")
    requirement_name: Optional[str] = Field(None, description="需求名称(模糊查询)")
    requirement_type: Optional[str] = Field(None, description="需求类型")
    priority: Optional[str] = Field(None, description="优先级")
    status: Optional[str] = Field(None, description="状态")
    module: Optional[str] = Field(None, description="所属模块")
    created_by: Optional[int] = Field(None, description="创建人")
    page_num: int = Field(1, ge=1, description="页码")
    page_size: int = Field(10, ge=1, le=100, description="每页数量")


class RequirementAnalysisGenerateVO(BaseModel):
    """AI生成需求分析VO"""
    project_id: int = Field(..., description="项目ID")
    requirement_summary: str = Field(..., description="需求摘要")
    requirement_description: str = Field(..., description="需求描述")
    module: Optional[str] = Field(None, description="所属模块")
    requirement_type: str = Field("functional", description="需求类型")
    thread_id: Optional[str] = Field(None, description="会话ID")
    auto_save: bool = Field(False, description="是否自动保存")

