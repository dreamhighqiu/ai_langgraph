"""
需求分析 Schemas

定义需求分析相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import RequirementAnalysisStatus


class RequirementAnalysisBase(BaseModel):
    """需求分析基础 Schema"""
    title: str = Field(..., max_length=500, description="需求分析标题")
    description: Optional[str] = Field(None, description="需求简要描述")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    owner_id: Optional[UUID] = Field(None, description="负责人 ID")


class RequirementAnalysisCreate(RequirementAnalysisBase):
    """创建需求分析请求 Schema"""
    document_url: Optional[str] = Field(None, max_length=1000, description="需求文档 URL")
    document_type: Optional[str] = Field(None, max_length=100, description="文档类型")
    
    # AI 分析选项
    use_rag: bool = Field(default=False, description="是否使用 RAG 检索")
    rag_query: Optional[str] = Field(None, description="RAG 检索查询")
    
    # 可选：用户提供的额外信息
    additional_context: Optional[str] = Field(None, description="额外上下文信息")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "电商平台用户管理模块需求分析",
            "description": "分析用户注册、登录、个人信息管理等功能需求",
            "document_url": "https://minio.example.com/docs/requirement.pdf",
            "document_type": "application/pdf",
            "use_rag": True,
            "tags": ["用户管理", "V2.0"],
        }
    })


class RequirementAnalysisUpdate(BaseModel):
    """更新需求分析请求 Schema"""
    title: Optional[str] = Field(None, max_length=500, description="需求分析标题")
    description: Optional[str] = Field(None, description="需求简要描述")
    status: Optional[RequirementAnalysisStatus] = Field(None, description="分析状态")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    owner_id: Optional[UUID] = Field(None, description="负责人 ID")
    
    # AI 分析结果（支持手动编辑）
    executive_summary: Optional[str] = Field(None, description="需求概述")
    functional_requirements: Optional[str] = Field(None, description="功能需求分析")
    non_functional_requirements: Optional[str] = Field(None, description="非功能需求分析")
    user_stories: Optional[List[dict]] = Field(None, description="用户故事列表")
    acceptance_criteria: Optional[List[dict]] = Field(None, description="验收标准列表")
    dependencies: Optional[List[dict]] = Field(None, description="依赖关系")
    risks: Optional[List[dict]] = Field(None, description="风险评估")
    recommendations: Optional[List[dict]] = Field(None, description="建议和改进意见")
    priority_analysis: Optional[dict] = Field(None, description="优先级分析")
    effort_estimation: Optional[dict] = Field(None, description="工作量评估")
    
    # 质量评分
    quality_score: Optional[float] = Field(None, ge=0, le=100, description="需求文档质量评分")
    completeness_score: Optional[float] = Field(None, ge=0, le=100, description="完整性评分")
    clarity_score: Optional[float] = Field(None, ge=0, le=100, description="清晰度评分")
    consistency_score: Optional[float] = Field(None, ge=0, le=100, description="一致性评分")
    
    custom_fields: Optional[dict] = Field(None, description="自定义字段")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "approved",
            "quality_score": 85.5,
            "tags": ["已评审", "高优先级"],
        }
    })


class UserStoryInfo(BaseModel):
    """用户故事信息"""
    role: str = Field(..., description="用户角色")
    action: str = Field(..., description="想要的功能")
    benefit: str = Field(..., description="获得的价值")
    priority: Optional[str] = Field(None, description="优先级")
    acceptance_criteria: Optional[List[str]] = Field(default_factory=list, description="验收标准")
    
    model_config = ConfigDict(from_attributes=True)


class AcceptanceCriteriaInfo(BaseModel):
    """验收标准信息"""
    criterion: str = Field(..., description="验收标准描述")
    priority: Optional[str] = Field(None, description="优先级")
    category: Optional[str] = Field(None, description="分类")
    
    model_config = ConfigDict(from_attributes=True)


class DependencyInfo(BaseModel):
    """依赖关系信息"""
    dependency_type: str = Field(..., description="依赖类型")
    description: str = Field(..., description="依赖描述")
    impact: Optional[str] = Field(None, description="影响程度")
    
    model_config = ConfigDict(from_attributes=True)


class RiskInfo(BaseModel):
    """风险信息"""
    risk_type: str = Field(..., description="风险类型")
    description: str = Field(..., description="风险描述")
    probability: Optional[str] = Field(None, description="发生概率")
    impact: Optional[str] = Field(None, description="影响程度")
    mitigation: Optional[str] = Field(None, description="缓解措施")
    
    model_config = ConfigDict(from_attributes=True)


class RequirementAnalysisInfo(RequirementAnalysisBase):
    """需求分析详细信息 Schema"""
    id: UUID = Field(..., description="需求分析 ID")
    identifier: str = Field(..., description="需求分析标识符")
    project_id: UUID = Field(..., description="所属项目 ID")
    
    # 文档信息
    document_url: Optional[str] = Field(None, description="需求文档 URL")
    document_type: Optional[str] = Field(None, description="文档类型")
    
    # AI 分析结果
    executive_summary: Optional[str] = Field(None, description="需求概述")
    functional_requirements: Optional[str] = Field(None, description="功能需求分析")
    non_functional_requirements: Optional[str] = Field(None, description="非功能需求分析")
    user_stories: Optional[List[dict]] = Field(default_factory=list, description="用户故事列表")
    acceptance_criteria: Optional[List[dict]] = Field(default_factory=list, description="验收标准列表")
    dependencies: Optional[List[dict]] = Field(default_factory=list, description="依赖关系")
    risks: Optional[List[dict]] = Field(default_factory=list, description="风险评估")
    recommendations: Optional[List[dict]] = Field(default_factory=list, description="建议和改进意见")
    priority_analysis: Optional[dict] = Field(None, description="优先级分析")
    effort_estimation: Optional[dict] = Field(None, description="工作量评估")
    
    # 质量评分
    quality_score: Optional[float] = Field(None, description="需求文档质量评分")
    completeness_score: Optional[float] = Field(None, description="完整性评分")
    clarity_score: Optional[float] = Field(None, description="清晰度评分")
    consistency_score: Optional[float] = Field(None, description="一致性评分")
    
    # RAG 信息
    rag_context: Optional[dict] = Field(None, description="RAG 检索的上下文信息")
    used_rag: bool = Field(default=False, description="是否使用了 RAG 检索")
    
    # 状态和元数据
    status: RequirementAnalysisStatus = Field(..., description="分析状态")
    custom_fields: Optional[dict] = Field(default_factory=dict, description="自定义字段")
    
    # 用户信息
    created_by: UUID = Field(..., description="创建者 ID")
    version: int = Field(..., description="版本号")
    
    # 时间戳
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "identifier": "REQ-ANAL-0001",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "电商平台用户管理模块需求分析",
                "description": "分析用户注册、登录、个人信息管理等功能需求",
                "executive_summary": "本需求文档描述了电商平台用户管理模块的核心功能...",
                "quality_score": 85.5,
                "completeness_score": 88.0,
                "clarity_score": 82.0,
                "consistency_score": 87.0,
                "status": "approved",
                "used_rag": True,
                "version": 1,
            }
        }
    )


class RequirementAnalysisMinifiedInfo(BaseModel):
    """需求分析精简信息 Schema（用于列表展示）"""
    id: UUID = Field(..., description="需求分析 ID")
    identifier: str = Field(..., description="需求分析标识符")
    title: str = Field(..., description="需求分析标题")
    description: Optional[str] = Field(None, description="需求简要描述")
    status: RequirementAnalysisStatus = Field(..., description="分析状态")
    quality_score: Optional[float] = Field(None, description="质量评分")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


class RequirementAnalysisDownloadResponse(BaseModel):
    """需求分析报告下载响应"""
    success: bool = Field(..., description="是否成功")
    download_url: Optional[str] = Field(None, description="下载链接")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    expires_at: Optional[datetime] = Field(None, description="链接过期时间")
    message: Optional[str] = Field(None, description="消息")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "download_url": "https://minio.example.com/reports/req-anal-0001.pdf",
            "file_name": "需求分析报告_REQ-ANAL-0001.pdf",
            "file_size": 1048576,
            "expires_at": "2026-01-09T10:00:00",
        }
    })

