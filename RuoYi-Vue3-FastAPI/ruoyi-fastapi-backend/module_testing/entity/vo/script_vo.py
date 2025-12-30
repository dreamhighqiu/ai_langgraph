"""
测试脚本视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ScriptModel(BaseModel):
    """脚本模型"""
    model_config = ConfigDict(from_attributes=True)
    
    script_id: Optional[int] = Field(None, description='脚本ID')
    project_id: int = Field(..., description='项目ID')
    project_name: Optional[str] = Field(None, description='项目名称')
    script_name: str = Field(..., max_length=100, description='脚本名称')
    script_type: str = Field(..., description='脚本类型：k6/playwright/api')
    script_content: Optional[str] = Field(None, description='脚本内容')
    script_file_path: Optional[str] = Field(None, description='MinIO存储路径')
    version: Optional[str] = Field('1.0.0', description='版本号')
    config: Optional[dict] = Field(None, description='配置参数')
    agent_id: Optional[str] = Field(None, description='Agent ID')
    generation_prompt: Optional[str] = Field(None, description='生成提示词')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')
    status: Optional[str] = Field('0', description='状态')
    remark: Optional[str] = Field(None, description='备注')


class ScriptPageQueryModel(BaseModel):
    """脚本分页查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    script_type: Optional[str] = Field(None, description='脚本类型')
    status: Optional[str] = Field(None, description='状态')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')


class AddScriptModel(BaseModel):
    """新增脚本模型"""
    project_id: int = Field(..., description='项目ID')
    script_name: str = Field(..., max_length=100, description='脚本名称')
    script_type: str = Field(..., description='脚本类型：k6/playwright/api')
    script_content: Optional[str] = Field(None, description='脚本内容')
    config: Optional[dict] = Field(None, description='配置参数')
    remark: Optional[str] = Field(None, description='备注')


class EditScriptModel(BaseModel):
    """编辑脚本模型"""
    script_id: int = Field(..., description='脚本ID')
    script_name: Optional[str] = Field(None, max_length=100, description='脚本名称')
    script_content: Optional[str] = Field(None, description='脚本内容')
    config: Optional[dict] = Field(None, description='配置参数')
    status: Optional[str] = Field(None, description='状态')
    remark: Optional[str] = Field(None, description='备注')


class DeleteScriptModel(BaseModel):
    """删除脚本模型"""
    script_ids: str = Field(..., description='脚本ID列表，逗号分隔')


class GenerateScriptModel(BaseModel):
    """AI生成脚本请求模型"""
    project_id: int = Field(..., description='项目ID')
    script_name: str = Field(..., max_length=100, description='脚本名称')
    script_type: str = Field(..., description='脚本类型: k6/playwright/api')
    prompt: str = Field(..., min_length=10, description='生成提示词')
    config: Optional[dict] = Field(None, description='配置参数')


class ExecuteScriptModel(BaseModel):
    """执行脚本请求模型"""
    script_id: int = Field(..., description='脚本ID')
    config: Optional[dict] = Field(None, description='执行配置')
    execution_type: Optional[str] = Field('manual', description='执行类型')


class GenerateScriptResponse(BaseModel):
    """AI生成脚本响应模型"""
    script_id: int = Field(..., description='脚本ID')
    script_content: str = Field(..., description='脚本内容')
    file_path: Optional[str] = Field(None, description='存储路径')
    thread_id: Optional[str] = Field(None, description='线程ID')
    agent_id: Optional[str] = Field(None, description='Agent ID')

