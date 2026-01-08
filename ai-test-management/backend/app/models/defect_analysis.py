"""
缺陷分析模型

定义缺陷分析报告相关的表结构
"""

from sqlalchemy import ForeignKey, Integer, String, Text, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.schemas.enums import DefectAnalysisStatus, DefectSeverity


class DefectAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    缺陷分析表
    
    存储 AI 生成的缺陷分析报告信息
    """
    __tablename__ = "defect_analyses"
    __table_args__ = {"comment": "缺陷分析表"}
    
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="所属项目 ID"
    )
    
    identifier: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="缺陷分析标识符，如 DEF-ANAL-1234"
    )
    
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="缺陷分析标题"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="缺陷简要描述"
    )
    
    # 缺陷文档信息
    document_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="原始缺陷报告文档 URL（MinIO）"
    )
    
    document_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="文档类型（PDF, Word, Excel, etc.）"
    )
    
    # AI 分析结果
    executive_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="缺陷分析概述"
    )
    
    root_cause_analysis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="根因分析"
    )
    
    impact_analysis: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="影响分析"
    )
    
    # 缺陷分类统计
    defect_categories: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="缺陷分类统计（功能缺陷、性能缺陷、UI缺陷等）"
    )
    
    severity_distribution: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="严重程度分布统计"
    )
    
    module_distribution: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="模块分布统计"
    )
    
    # 缺陷趋势
    defect_trends: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="缺陷趋势分析（新增、修复、重开等）"
    )
    
    # 详细缺陷列表
    defects: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="缺陷详细列表"
    )
    
    # 关键问题和建议
    critical_issues: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="关键问题列表"
    )
    
    recommendations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="改进建议列表"
    )
    
    preventive_measures: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="预防措施建议"
    )
    
    # 质量指标
    defect_density: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="缺陷密度（每千行代码缺陷数）"
    )
    
    fix_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="修复率（%）"
    )
    
    reopen_rate: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="重开率（%）"
    )
    
    avg_fix_time: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="平均修复时间（小时）"
    )
    
    # 质量评分
    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="整体质量评分（0-100）"
    )
    
    severity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="严重性评分（0-100）"
    )
    
    coverage_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="覆盖度评分（0-100）"
    )
    
    # RAG 增强信息
    rag_context: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="RAG 检索的上下文信息"
    )
    
    used_rag: Mapped[bool] = mapped_column(
        default=False,
        nullable=False,
        comment="是否使用了 RAG 检索"
    )
    
    # 状态和标签
    status: Mapped[DefectAnalysisStatus] = mapped_column(
        SQLEnum(DefectAnalysisStatus),
        default=DefectAnalysisStatus.DRAFT,
        nullable=False,
        index=True,
        comment="分析状态"
    )
    
    tags: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="标签列表"
    )
    
    # 自定义字段
    custom_fields: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="自定义字段"
    )
    
    # 创建者和负责人
    created_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="创建者 ID"
    )
    
    owner_id: Mapped[UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="负责人 ID"
    )
    
    # 版本号
    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
        comment="版本号"
    )
    
    # 关系
    project: Mapped["Project"] = relationship("Project", back_populates="defect_analyses")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    owner: Mapped["User | None"] = relationship(
        "User", foreign_keys=[owner_id]
    )
    
    def __repr__(self) -> str:
        return f"<DefectAnalysis(id={self.id}, identifier={self.identifier}, title={self.title})>"

