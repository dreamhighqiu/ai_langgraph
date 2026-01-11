"""
UI自动化测试脚本视图对象(VO - View Object)
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class UIScriptModel(BaseModel):
    """UI脚本模型"""
    model_config = ConfigDict(from_attributes=True)
    
    script_id: Optional[int] = Field(None, description='脚本ID')
    project_id: int = Field(..., description='项目ID')
    project_name: Optional[str] = Field(None, description='项目名称')
    requirement_id: Optional[int] = Field(None, description='需求ID')
    requirement_name: Optional[str] = Field(None, description='需求名称')
    script_name: str = Field(..., description='脚本名称')
    script_type: str = Field('playwright', description='脚本类型：playwright')
    language: str = Field('typescript', description='脚本语言：typescript/javascript')
    browser: str = Field('chromium', description='目标浏览器：chromium/firefox/webkit')
    script_content: Optional[str] = Field(None, description='脚本内容')
    script_file_path: Optional[str] = Field(None, description='MinIO存储路径')
    version: str = Field('1.0.0', description='版本号')
    config: Optional[dict] = Field(None, description='配置参数')
    agent_id: Optional[str] = Field(None, description='Agent ID')
    generation_prompt: Optional[str] = Field(None, description='生成提示词')
    use_rag: str = Field('0', description='是否使用RAG（0否 1是）')
    status: str = Field('0', description='状态（0正常 1停用）')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class UIScriptPageQueryModel(BaseModel):
    """UI脚本分页查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    requirement_id: Optional[int] = Field(None, description='需求ID')
    script_name: Optional[str] = Field(None, description='脚本名称（模糊查询）')
    language: Optional[str] = Field(None, description='脚本语言')
    browser: Optional[str] = Field(None, description='目标浏览器')
    status: Optional[str] = Field(None, description='状态')
    agent_id: Optional[str] = Field(None, description='Agent ID')
    begin_time: Optional[str] = Field(None, description='开始时间')
    end_time: Optional[str] = Field(None, description='结束时间')


class AddUIScriptModel(BaseModel):
    """添加UI脚本模型"""
    project_id: int = Field(..., description='项目ID')
    requirement_id: Optional[int] = Field(None, description='需求ID')
    script_name: str = Field(..., description='脚本名称')
    language: str = Field('typescript', description='脚本语言：typescript/javascript')
    browser: str = Field('chromium', description='目标浏览器：chromium/firefox/webkit')
    script_content: Optional[str] = Field(None, description='脚本内容')
    script_file_path: Optional[str] = Field(None, description='MinIO存储路径')
    version: str = Field('1.0.0', description='版本号')
    config: Optional[dict] = Field(None, description='配置参数')
    agent_id: Optional[str] = Field(None, description='Agent ID')
    generation_prompt: Optional[str] = Field(None, description='生成提示词')
    use_rag: str = Field('0', description='是否使用RAG（0否 1是）')
    status: str = Field('0', description='状态（0正常 1停用）')
    remark: Optional[str] = Field(None, description='备注')


class EditUIScriptModel(BaseModel):
    """编辑UI脚本模型"""
    script_id: int = Field(..., description='脚本ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    language: Optional[str] = Field(None, description='脚本语言')
    browser: Optional[str] = Field(None, description='目标浏览器')
    script_content: Optional[str] = Field(None, description='脚本内容')
    script_file_path: Optional[str] = Field(None, description='MinIO存储路径')
    version: Optional[str] = Field(None, description='版本号')
    config: Optional[dict] = Field(None, description='配置参数')
    requirement_id: Optional[int] = Field(None, description='需求ID')
    status: Optional[str] = Field(None, description='状态')
    remark: Optional[str] = Field(None, description='备注')


class DeleteUIScriptModel(BaseModel):
    """删除UI脚本模型"""
    script_ids: list[int] = Field(..., description='脚本ID列表')


class ExecuteUIScriptModel(BaseModel):
    """执行UI脚本模型"""
    script_id: int = Field(..., description='脚本ID')
    execution_type: str = Field('manual', description='执行类型：manual/scheduled/ci')
    browser: str = Field('chromium', description='执行浏览器：chromium/firefox/webkit')
    headless: bool = Field(True, description='是否无头模式')
    config: Optional[dict] = Field(None, description='执行配置')
    env_vars: Optional[dict] = Field(None, description='环境变量')
    timeout: Optional[int] = Field(None, description='超时时间（毫秒）')


class GenerateUIScriptModel(BaseModel):
    """生成UI脚本模型"""
    project_id: int = Field(..., description='项目ID')
    requirement_id: Optional[int] = Field(None, description='需求ID')
    script_name: str = Field(..., description='脚本名称')
    generation_prompt: str = Field(..., description='生成提示词/需求描述')
    language: str = Field('typescript', description='脚本语言：typescript/javascript')
    browser: str = Field('chromium', description='目标浏览器：chromium/firefox/webkit')
    agent_id: Optional[str] = Field(None, description='使用的Agent ID')
    config: Optional[dict] = Field(None, description='生成配置')
    use_rag: bool = Field(False, description='是否使用RAG知识库')


class GenerateUIScriptResponse(BaseModel):
    """生成UI脚本响应模型"""
    script_id: int = Field(..., description='脚本ID')
    script_name: str = Field(..., description='脚本名称')
    script_content: str = Field(..., description='生成的脚本内容')
    language: str = Field(..., description='脚本语言')
    browser: str = Field(..., description='目标浏览器')
    agent_id: Optional[str] = Field(None, description='使用的Agent ID')
    generation_time: Optional[datetime] = Field(None, description='生成时间')
    message: str = Field('', description='提示信息')


class UIExecutionResponse(BaseModel):
    """UI脚本执行响应模型"""
    execution_id: int = Field(..., description='执行ID')
    script_id: int = Field(..., description='脚本ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    execution_type: str = Field(..., description='执行类型')
    status: str = Field(..., description='执行状态：pending/running/success/failed')
    browser: str = Field(..., description='浏览器')
    headless: bool = Field(True, description='是否无头模式')
    start_time: Optional[datetime] = Field(None, description='开始时间')
    end_time: Optional[datetime] = Field(None, description='结束时间')
    duration: Optional[int] = Field(None, description='执行时长（毫秒）')
    result: Optional[dict] = Field(None, description='执行结果')
    error_message: Optional[str] = Field(None, description='错误信息')
    executor: Optional[str] = Field(None, description='执行者')
    create_time: Optional[datetime] = Field(None, description='创建时间')


class UIReportResponse(BaseModel):
    """UI测试报告响应模型"""
    report_id: int = Field(..., description='报告ID')
    execution_id: int = Field(..., description='执行ID')
    report_name: str = Field(..., description='报告名称')
    report_type: str = Field(..., description='报告类型：html/json/junit')
    file_path: Optional[str] = Field(None, description='MinIO文件路径')
    file_size: Optional[int] = Field(None, description='文件大小（字节）')
    status: str = Field(..., description='状态')
    create_time: Optional[datetime] = Field(None, description='创建时间')


class UIScriptResponse(BaseModel):
    """UI脚本通用响应模型"""
    success: bool = Field(..., description='是否成功')
    script_id: Optional[int] = Field(None, description='脚本ID')
    script_name: Optional[str] = Field(None, description='脚本名称')
    script_content: Optional[str] = Field(None, description='脚本内容')
    message: str = Field('', description='提示信息')
    error: Optional[str] = Field(None, description='错误信息')
    data: Optional[dict] = Field(None, description='附加数据')


# 兼容性别名（用于 ui_automation_service）
UIScriptGenerateRequest = GenerateUIScriptModel
UIScriptExecuteRequest = ExecuteUIScriptModel
