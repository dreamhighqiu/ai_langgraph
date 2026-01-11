"""
测试执行记录视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ExecutionModel(BaseModel):
    """执行记录模型"""
    model_config = ConfigDict(from_attributes=True)
    
    execution_id: Optional[int] = Field(None, description='执行ID')
    script_id: int = Field(..., description='脚本ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    script_type: Optional[str] = Field(None, description='脚本类型')
    project_name: Optional[str] = Field(None, description='项目名称')
    execution_type: Optional[str] = Field('manual', description='执行类型')
    execution_status: Optional[str] = Field('pending', description='执行状态')
    start_time: Optional[datetime] = Field(None, description='开始时间')
    end_time: Optional[datetime] = Field(None, description='结束时间')
    duration: Optional[int] = Field(None, description='执行时长(秒)')
    thread_id: Optional[str] = Field(None, description='线程ID')
    agent_id: Optional[str] = Field(None, description='Agent ID')
    config: Optional[dict] = Field(None, description='执行配置')
    result: Optional[dict] = Field(None, description='执行结果')
    error_msg: Optional[str] = Field(None, description='错误信息')
    executor: Optional[str] = Field(None, description='执行者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_time: Optional[datetime] = Field(None, description='更新时间')


class ExecutionPageQueryModel(BaseModel):
    """执行记录分页查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    script_id: Optional[int] = Field(None, description='脚本ID')
    script_type: Optional[str] = Field(None, description='脚本类型')
    project_id: Optional[int] = Field(None, description='项目ID')
    execution_status: Optional[str] = Field(None, description='执行状态')
    execution_type: Optional[str] = Field(None, description='执行类型')
    executor: Optional[str] = Field(None, description='执行者')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')


class ExecutionDetailModel(BaseModel):
    """执行详情模型"""
    model_config = ConfigDict(from_attributes=True)
    
    execution_id: int = Field(..., description='执行ID')
    script_id: int = Field(..., description='脚本ID')
    script_name: str = Field(..., description='脚本名称')
    script_type: str = Field(..., description='脚本类型')
    script_content: Optional[str] = Field(None, description='脚本内容')
    project_name: str = Field(..., description='项目名称')
    execution_type: str = Field(..., description='执行类型')
    execution_status: str = Field(..., description='执行状态')
    start_time: Optional[datetime] = Field(None, description='开始时间')
    end_time: Optional[datetime] = Field(None, description='结束时间')
    duration: Optional[int] = Field(None, description='执行时长')
    config: Optional[dict] = Field(None, description='执行配置')
    result: Optional[dict] = Field(None, description='执行结果')
    error_msg: Optional[str] = Field(None, description='错误信息')
    executor: str = Field(..., description='执行者')
    logs: Optional[list] = Field(None, description='执行日志')
    reports: Optional[list] = Field(None, description='关联报告')


class CancelExecutionModel(BaseModel):
    """取消执行模型"""
    execution_id: int = Field(..., description='执行ID')
    reason: Optional[str] = Field(None, description='取消原因')

