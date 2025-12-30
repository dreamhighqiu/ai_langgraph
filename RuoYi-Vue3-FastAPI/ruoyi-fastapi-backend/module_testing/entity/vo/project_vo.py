"""
测试项目视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ProjectModel(BaseModel):
    """项目模型"""
    model_config = ConfigDict(from_attributes=True)
    
    project_id: Optional[int] = Field(None, description='项目ID')
    project_name: str = Field(..., max_length=100, description='项目名称')
    project_type: str = Field(..., description='项目类型：performance/ui/api')
    description: Optional[str] = Field(None, description='项目描述')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')
    status: Optional[str] = Field('0', description='状态：0正常 1停用')
    remark: Optional[str] = Field(None, description='备注')


class ProjectPageQueryModel(BaseModel):
    """项目分页查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    project_name: Optional[str] = Field(None, description='项目名称')
    project_type: Optional[str] = Field(None, description='项目类型')
    status: Optional[str] = Field(None, description='状态')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')


class AddProjectModel(BaseModel):
    """新增项目模型"""
    project_name: str = Field(..., max_length=100, description='项目名称')
    project_type: str = Field(..., description='项目类型：performance/ui/api')
    description: Optional[str] = Field(None, description='项目描述')
    status: Optional[str] = Field('0', description='状态')
    remark: Optional[str] = Field(None, description='备注')


class EditProjectModel(BaseModel):
    """编辑项目模型"""
    project_id: int = Field(..., description='项目ID')
    project_name: Optional[str] = Field(None, max_length=100, description='项目名称')
    project_type: Optional[str] = Field(None, description='项目类型')
    description: Optional[str] = Field(None, description='项目描述')
    status: Optional[str] = Field(None, description='状态')
    remark: Optional[str] = Field(None, description='备注')


class DeleteProjectModel(BaseModel):
    """删除项目模型"""
    project_ids: str = Field(..., description='项目ID列表，逗号分隔')

