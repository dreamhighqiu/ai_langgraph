"""
知识库视图对象（VO）
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class KnowledgeModel(BaseModel):
    """知识库模型"""
    model_config = ConfigDict(from_attributes=True)

    knowledge_id: Optional[int] = Field(None, description='知识库ID')
    project_id: int = Field(..., description='所属项目ID')
    knowledge_name: str = Field(..., max_length=100, description='知识库名称')
    collection_name: str = Field(..., max_length=255, description='Milvus Collection 名称')
    description: Optional[str] = Field(None, description='知识库描述')
    file_count: int = Field(0, description='文件数量')
    vector_count: int = Field(0, description='向量数量')
    status: str = Field('0', description='状态：0正常 1停用')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_by: Optional[str] = Field(None, description='更新者')
    update_time: Optional[datetime] = Field(None, description='更新时间')
    remark: Optional[str] = Field(None, description='备注')


class KnowledgeCreateModel(BaseModel):
    """创建知识库模型"""
    project_id: int = Field(..., description='所属项目ID')
    knowledge_name: str = Field(..., max_length=100, description='知识库名称')
    description: Optional[str] = Field(None, description='知识库描述')
    remark: Optional[str] = Field(None, description='备注')


class KnowledgeUpdateModel(BaseModel):
    """更新知识库模型"""
    knowledge_id: int = Field(..., description='知识库ID')
    knowledge_name: Optional[str] = Field(None, max_length=100, description='知识库名称')
    description: Optional[str] = Field(None, description='知识库描述')
    status: Optional[str] = Field(None, description='状态')
    remark: Optional[str] = Field(None, description='备注')


class KnowledgeQueryModel(BaseModel):
    """知识库查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    project_id: Optional[int] = Field(None, description='项目ID')
    knowledge_name: Optional[str] = Field(None, description='知识库名称')
    status: Optional[str] = Field(None, description='状态')


class KnowledgeDetailModel(KnowledgeModel):
    """知识库详情模型（包含项目信息）"""
    project_name: Optional[str] = Field(None, description='项目名称')


class KnowledgeStatsModel(BaseModel):
    """知识库统计模型"""
    file_count: int = Field(0, description='文件数量')
    vector_count: int = Field(0, description='向量数量')
    pending_count: int = Field(0, description='待处理文件数')
    processing_count: int = Field(0, description='处理中文件数')
    completed_count: int = Field(0, description='已完成文件数')
    failed_count: int = Field(0, description='失败文件数')


class KnowledgeFileModel(BaseModel):
    """知识库文件模型"""
    model_config = ConfigDict(from_attributes=True)

    file_id: Optional[int] = Field(None, description='文件ID')
    knowledge_id: int = Field(..., description='知识库ID')
    file_name: str = Field(..., max_length=255, description='文件名称')
    file_path: str = Field(..., max_length=500, description='文件存储路径')
    file_size: int = Field(0, description='文件大小')
    file_type: Optional[str] = Field(None, description='文件类型/格式（从文件名提取）')
    file_url: Optional[str] = Field(None, description='文件访问URL（预签名URL）')
    doc_id: Optional[str] = Field(None, description='LightRAG 文档ID')
    process_status: str = Field('pending', description='处理状态')
    process_progress: int = Field(0, description='处理进度')
    process_start_time: Optional[datetime] = Field(None, description='处理开始时间')
    process_end_time: Optional[datetime] = Field(None, description='处理结束时间')
    error_msg: Optional[str] = Field(None, description='错误信息')
    vector_count: int = Field(0, description='向量数量')
    create_by: Optional[str] = Field(None, description='创建者')
    create_time: Optional[datetime] = Field(None, description='创建时间')
    update_time: Optional[datetime] = Field(None, description='更新时间')


class KnowledgeFileQueryModel(BaseModel):
    """文件查询模型"""
    page_num: int = Field(1, ge=1, description='页码')
    page_size: int = Field(10, ge=1, le=100, description='每页数量')
    knowledge_id: Optional[int] = Field(None, description='知识库ID')
    file_name: Optional[str] = Field(None, description='文件名称')
    process_status: Optional[str] = Field(None, description='处理状态')


class KnowledgeFileUploadModel(BaseModel):
    """文件上传模型"""
    knowledge_id: int = Field(..., description='知识库ID')
    remark: Optional[str] = Field(None, description='备注')


class KnowledgeQueryRequestModel(BaseModel):
    """知识库查询请求模型"""
    query: str = Field(..., min_length=1, description='查询文本')
    mode: str = Field('hybrid', description='查询模式: naive/local/global/hybrid')
    top_k: Optional[int] = Field(None, description='返回结果数量')
    project_id: Optional[int] = Field(None, description='项目ID（可选，用于验证数据隔离）')


class KnowledgeQueryResponseModel(BaseModel):
    """知识库查询响应模型"""
    query: str = Field(..., description='查询文本')
    mode: str = Field(..., description='查询模式')
    answer: str = Field(..., description='回答内容')
    knowledge_id: int = Field(..., description='知识库ID')
    knowledge_name: str = Field(..., description='知识库名称')
    references: Optional[list] = Field(None, description='引用来源')


