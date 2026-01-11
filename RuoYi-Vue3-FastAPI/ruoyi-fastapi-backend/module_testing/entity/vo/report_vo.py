"""
测试报告视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class ReportModel(BaseModel):
    """报告模型"""
    model_config = ConfigDict(from_attributes=True)
    
    report_id: Optional[int] = Field(None, description='报告ID')
    execution_id: int = Field(..., description='执行ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    project_name: Optional[str] = Field(None, description='项目名称')
    report_name: str = Field(..., max_length=200, description='报告名称')
    report_type: str = Field(..., description='报告类型：html/pdf/json/allure')
    report_path: Optional[str] = Field(None, description='存储路径')
    report_size: Optional[int] = Field(None, description='报告大小(字节)')
    summary: Optional[dict] = Field(None, description='报告摘要')
    metrics: Optional[dict] = Field(None, description='关键指标')
    create_time: Optional[datetime] = Field(None, description='创建时间')


class ReportPageQueryModel(BaseModel):
    """报告分页查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    execution_id: Optional[int] = Field(None, description='执行ID')
    report_name: Optional[str] = Field(None, description='报告名称')
    report_type: Optional[str] = Field(None, description='报告类型')
    script_type: Optional[str] = Field(None, description='脚本类型')
    project_id: Optional[int] = Field(None, description='项目ID')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')


class ReportDetailModel(BaseModel):
    """报告详情模型"""
    model_config = ConfigDict(from_attributes=True)
    
    report_id: int = Field(..., description='报告ID')
    execution_id: int = Field(..., description='执行ID')
    script_name: str = Field(..., description='脚本名称')
    script_type: str = Field(..., description='脚本类型')
    project_name: str = Field(..., description='项目名称')
    report_name: str = Field(..., description='报告名称')
    report_type: str = Field(..., description='报告类型')
    report_path: Optional[str] = Field(None, description='存储路径')
    report_size: Optional[int] = Field(None, description='报告大小')
    report_content: Optional[str] = Field(None, description='报告内容')
    summary: Optional[dict] = Field(None, description='报告摘要')
    metrics: Optional[dict] = Field(None, description='关键指标')
    create_time: datetime = Field(..., description='创建时间')
    execution_status: str = Field(..., description='执行状态')
    duration: Optional[int] = Field(None, description='执行时长')


class CompareReportsModel(BaseModel):
    """报告对比模型"""
    report_ids: list[int] = Field(..., min_length=2, max_length=5, description='报告ID列表')


class CompareReportsResponse(BaseModel):
    """报告对比响应模型"""
    reports: list[ReportDetailModel] = Field(..., description='报告列表')
    comparison: dict = Field(..., description='对比结果')
    charts: Optional[dict] = Field(None, description='图表数据')

