"""
测试需求视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field


class RequirementModel(BaseModel):
    """需求模型"""
    requirement_id: Optional[int] = Field(None, description='需求ID')
    project_id: int = Field(..., description='项目ID')
    requirement_name: str = Field(..., max_length=200, description='需求名称')
    requirement_type: str = Field(..., description='需求类型：performance/ui/api')
    description: Optional[str] = Field(None, description='需求描述')
    acceptance_criteria: Optional[dict] = Field(None, description='验收标准')
    priority: str = Field('medium', description='优先级：low/medium/high')
    status: str = Field('0', description='状态（0待处理 1进行中 2已完成 3已关闭）')
    tags: Optional[List[str]] = Field(None, description='标签')
    attachments: Optional[List[dict]] = Field(None, description='附件')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')

    class Config:
        from_attributes = True


class RequirementPageQueryModel(BaseModel):
    """需求分页查询模型"""
    page_num: int = Field(1, description='页码')
    page_size: int = Field(10, description='每页数量')
    requirement_name: Optional[str] = Field(None, description='需求名称')
    requirement_type: Optional[str] = Field(None, description='需求类型')
    project_id: Optional[int] = Field(None, description='项目ID')
    priority: Optional[str] = Field(None, description='优先级')
    status: Optional[str] = Field(None, description='状态')
    create_by: Optional[str] = Field(None, description='创建者')


class RequirementAddModel(BaseModel):
    """新增需求模型"""
    project_id: int = Field(..., description='项目ID')
    requirement_name: str = Field(..., max_length=200, description='需求名称')
    requirement_type: str = Field(..., description='需求类型：performance/ui/api')
    description: Optional[str] = Field(None, description='需求描述')
    acceptance_criteria: Optional[dict] = Field(None, description='验收标准')
    priority: str = Field('medium', description='优先级')
    tags: Optional[List[str]] = Field(None, description='标签')
    attachments: Optional[List[dict]] = Field(None, description='附件')
    remark: Optional[str] = Field(None, description='备注')


class RequirementUpdateModel(BaseModel):
    """更新需求模型"""
    requirement_id: int = Field(..., description='需求ID')
    requirement_name: Optional[str] = Field(None, max_length=200, description='需求名称')
    requirement_type: Optional[str] = Field(None, description='需求类型')
    description: Optional[str] = Field(None, description='需求描述')
    acceptance_criteria: Optional[dict] = Field(None, description='验收标准')
    priority: Optional[str] = Field(None, description='优先级')
    status: Optional[str] = Field(None, description='状态')
    tags: Optional[List[str]] = Field(None, description='标签')
    attachments: Optional[List[dict]] = Field(None, description='附件')
    remark: Optional[str] = Field(None, description='备注')


class GenerateScriptFromRequirementModel(BaseModel):
    """从需求生成脚本模型"""
    requirement_id: int = Field(..., description='需求ID')
    config: Optional[dict] = Field(None, description='生成配置')
    use_rag: bool = Field(True, description='是否使用RAG增强')


class AnalyzeRequirementModel(BaseModel):
    """分析需求模型"""
    requirement_id: int = Field(..., description='需求ID')
    analyze_type: str = Field('feasibility', description='分析类型：feasibility/complexity/risk')

