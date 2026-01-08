"""
缺陷分析 Schemas

定义缺陷分析相关的数据传输对象
"""

from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.enums import (
    DefectAnalysisStatus,
    DefectSeverity,
    DefectPriority,
    DefectType
)


class DefectAnalysisBase(BaseModel):
    """缺陷分析基础 Schema"""
    title: str = Field(..., max_length=500, description="缺陷分析标题")
    description: Optional[str] = Field(None, description="缺陷简要描述")
    severity: Optional[DefectSeverity] = Field(None, description="严重程度")
    priority: Optional[DefectPriority] = Field(None, description="优先级")
    defect_type: Optional[DefectType] = Field(None, description="缺陷类型")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    owner_id: Optional[UUID] = Field(None, description="负责人 ID")


class DefectAnalysisCreate(DefectAnalysisBase):
    """创建缺陷分析请求 Schema"""
    document_url: Optional[str] = Field(None, max_length=1000, description="缺陷报告文档 URL")
    document_type: Optional[str] = Field(None, max_length=100, description="文档类型")
    
    # AI 分析选项
    use_rag: bool = Field(default=False, description="是否使用 RAG 检索")
    rag_query: Optional[str] = Field(None, description="RAG 检索查询")
    
    # 可选：用户提供的额外信息
    additional_context: Optional[str] = Field(None, description="额外上下文信息")
    
    # 关联的需求或测试用例
    related_requirement_ids: Optional[List[UUID]] = Field(default_factory=list, description="关联的需求 ID")
    related_testcase_ids: Optional[List[UUID]] = Field(default_factory=list, description="关联的测试用例 ID")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "title": "用户登录模块缺陷分析",
            "description": "分析用户登录失败的相关缺陷",
            "document_url": "https://minio.example.com/docs/defect-report.pdf",
            "document_type": "application/pdf",
            "severity": "high",
            "priority": "urgent",
            "defect_type": "functional",
            "use_rag": True,
            "tags": ["登录", "认证"],
        }
    })


class DefectAnalysisUpdate(BaseModel):
    """更新缺陷分析请求 Schema"""
    title: Optional[str] = Field(None, max_length=500, description="缺陷分析标题")
    description: Optional[str] = Field(None, description="缺陷简要描述")
    severity: Optional[DefectSeverity] = Field(None, description="严重程度")
    priority: Optional[DefectPriority] = Field(None, description="优先级")
    defect_type: Optional[DefectType] = Field(None, description="缺陷类型")
    status: Optional[DefectAnalysisStatus] = Field(None, description="分析状态")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    owner_id: Optional[UUID] = Field(None, description="负责人 ID")
    
    # AI 分析结果（支持手动编辑）
    executive_summary: Optional[str] = Field(None, description="缺陷概述")
    defect_classification: Optional[dict] = Field(None, description="缺陷分类分析")
    root_cause_analysis: Optional[str] = Field(None, description="根本原因分析")
    impact_analysis: Optional[str] = Field(None, description="影响分析")
    reproduction_steps: Optional[List[dict]] = Field(None, description="复现步骤")
    affected_modules: Optional[List[dict]] = Field(None, description="受影响的模块")
    fix_suggestions: Optional[List[dict]] = Field(None, description="修复建议")
    test_recommendations: Optional[List[dict]] = Field(None, description="测试建议")
    prevention_measures: Optional[List[dict]] = Field(None, description="预防措施")
    similar_defects: Optional[List[dict]] = Field(None, description="相似缺陷")
    
    # 趋势分析
    trend_analysis: Optional[dict] = Field(None, description="缺陷趋势分析")
    frequency_analysis: Optional[dict] = Field(None, description="发生频率分析")
    
    # 质量评分
    quality_score: Optional[float] = Field(None, ge=0, le=100, description="缺陷报告质量评分")
    completeness_score: Optional[float] = Field(None, ge=0, le=100, description="完整性评分")
    clarity_score: Optional[float] = Field(None, ge=0, le=100, description="清晰度评分")
    actionability_score: Optional[float] = Field(None, ge=0, le=100, description="可操作性评分")
    
    custom_fields: Optional[dict] = Field(None, description="自定义字段")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "status": "approved",
            "severity": "critical",
            "priority": "urgent",
            "quality_score": 82.0,
            "tags": ["已确认", "待修复"],
        }
    })


class ReproductionStepInfo(BaseModel):
    """复现步骤信息"""
    step_number: int = Field(..., description="步骤序号")
    action: str = Field(..., description="操作步骤")
    expected_result: Optional[str] = Field(None, description="预期结果")
    actual_result: Optional[str] = Field(None, description="实际结果")
    
    model_config = ConfigDict(from_attributes=True)


class AffectedModuleInfo(BaseModel):
    """受影响模块信息"""
    module_name: str = Field(..., description="模块名称")
    impact_level: Optional[str] = Field(None, description="影响程度")
    description: Optional[str] = Field(None, description="影响描述")
    
    model_config = ConfigDict(from_attributes=True)


class FixSuggestionInfo(BaseModel):
    """修复建议信息"""
    suggestion: str = Field(..., description="修复建议描述")
    priority: Optional[str] = Field(None, description="优先级")
    estimated_effort: Optional[str] = Field(None, description="预估工作量")
    technical_approach: Optional[str] = Field(None, description="技术方案")
    
    model_config = ConfigDict(from_attributes=True)


class TestRecommendationInfo(BaseModel):
    """测试建议信息"""
    test_type: str = Field(..., description="测试类型")
    description: str = Field(..., description="测试建议描述")
    priority: Optional[str] = Field(None, description="优先级")
    
    model_config = ConfigDict(from_attributes=True)


class PreventionMeasureInfo(BaseModel):
    """预防措施信息"""
    measure: str = Field(..., description="预防措施描述")
    category: Optional[str] = Field(None, description="措施类别")
    implementation_guide: Optional[str] = Field(None, description="实施指南")
    
    model_config = ConfigDict(from_attributes=True)


class SimilarDefectInfo(BaseModel):
    """相似缺陷信息"""
    defect_id: Optional[str] = Field(None, description="缺陷 ID")
    title: str = Field(..., description="缺陷标题")
    similarity_score: Optional[float] = Field(None, ge=0, le=1, description="相似度评分")
    reference_url: Optional[str] = Field(None, description="参考链接")
    
    model_config = ConfigDict(from_attributes=True)


class DefectAnalysisInfo(DefectAnalysisBase):
    """缺陷分析详细信息 Schema"""
    id: UUID = Field(..., description="缺陷分析 ID")
    identifier: str = Field(..., description="缺陷分析标识符")
    project_id: UUID = Field(..., description="所属项目 ID")
    
    # 文档信息
    document_url: Optional[str] = Field(None, description="缺陷报告文档 URL")
    document_type: Optional[str] = Field(None, description="文档类型")
    
    # AI 分析结果
    executive_summary: Optional[str] = Field(None, description="缺陷概述")
    defect_classification: Optional[dict] = Field(None, description="缺陷分类分析")
    root_cause_analysis: Optional[str] = Field(None, description="根本原因分析")
    impact_analysis: Optional[str] = Field(None, description="影响分析")
    reproduction_steps: Optional[List[dict]] = Field(default_factory=list, description="复现步骤")
    affected_modules: Optional[List[dict]] = Field(default_factory=list, description="受影响的模块")
    fix_suggestions: Optional[List[dict]] = Field(default_factory=list, description="修复建议")
    test_recommendations: Optional[List[dict]] = Field(default_factory=list, description="测试建议")
    prevention_measures: Optional[List[dict]] = Field(default_factory=list, description="预防措施")
    similar_defects: Optional[List[dict]] = Field(default_factory=list, description="相似缺陷")
    
    # 趋势分析
    trend_analysis: Optional[dict] = Field(None, description="缺陷趋势分析")
    frequency_analysis: Optional[dict] = Field(None, description="发生频率分析")
    
    # 质量评分
    quality_score: Optional[float] = Field(None, description="缺陷报告质量评分")
    completeness_score: Optional[float] = Field(None, description="完整性评分")
    clarity_score: Optional[float] = Field(None, description="清晰度评分")
    actionability_score: Optional[float] = Field(None, description="可操作性评分")
    
    # RAG 信息
    rag_context: Optional[dict] = Field(None, description="RAG 检索的上下文信息")
    used_rag: bool = Field(default=False, description="是否使用了 RAG 检索")
    
    # 关联信息
    related_requirement_ids: Optional[List[UUID]] = Field(default_factory=list, description="关联的需求 ID")
    related_testcase_ids: Optional[List[UUID]] = Field(default_factory=list, description="关联的测试用例 ID")
    
    # 状态和元数据
    status: DefectAnalysisStatus = Field(..., description="分析状态")
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
                "identifier": "DEF-ANAL-0001",
                "project_id": "123e4567-e89b-12d3-a456-426614174001",
                "title": "用户登录模块缺陷分析",
                "description": "分析用户登录失败的相关缺陷",
                "executive_summary": "本缺陷报告详细分析了用户登录失败的原因...",
                "severity": "critical",
                "priority": "urgent",
                "defect_type": "functional",
                "quality_score": 82.0,
                "completeness_score": 85.0,
                "clarity_score": 80.0,
                "actionability_score": 81.0,
                "status": "approved",
                "used_rag": True,
                "version": 1,
            }
        }
    )


class DefectAnalysisMinifiedInfo(BaseModel):
    """缺陷分析精简信息 Schema（用于列表展示）"""
    id: UUID = Field(..., description="缺陷分析 ID")
    identifier: str = Field(..., description="缺陷分析标识符")
    title: str = Field(..., description="缺陷分析标题")
    description: Optional[str] = Field(None, description="缺陷简要描述")
    severity: Optional[DefectSeverity] = Field(None, description="严重程度")
    priority: Optional[DefectPriority] = Field(None, description="优先级")
    defect_type: Optional[DefectType] = Field(None, description="缺陷类型")
    status: DefectAnalysisStatus = Field(..., description="分析状态")
    quality_score: Optional[float] = Field(None, description="质量评分")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")
    
    model_config = ConfigDict(from_attributes=True)


class DefectAnalysisDownloadResponse(BaseModel):
    """缺陷分析报告下载响应"""
    success: bool = Field(..., description="是否成功")
    download_url: Optional[str] = Field(None, description="下载链接")
    file_name: Optional[str] = Field(None, description="文件名")
    file_size: Optional[int] = Field(None, description="文件大小（字节）")
    expires_at: Optional[datetime] = Field(None, description="链接过期时间")
    message: Optional[str] = Field(None, description="消息")
    
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "success": True,
            "download_url": "https://minio.example.com/reports/def-anal-0001.pdf",
            "file_name": "缺陷分析报告_DEF-ANAL-0001.pdf",
            "file_size": 1048576,
            "expires_at": "2026-01-09T10:00:00",
        }
    })

