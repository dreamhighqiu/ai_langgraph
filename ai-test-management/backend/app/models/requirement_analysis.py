"""
需求分析模型

定义需求分析报告相关的表结构
"""

from sqlalchemy import ForeignKey, Integer, String, Text, Enum as SQLEnum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
from app.schemas.enums import Priority, RequirementAnalysisStatus


class RequirementAnalysis(Base, UUIDMixin, TimestampMixin):
    """
    需求分析表
    
    存储 AI 生成的需求分析报告信息
    """
    __tablename__ = "requirement_analyses"
    __table_args__ = {"comment": "需求分析表"}
    
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
        comment="需求分析标识符，如 REQ-ANAL-1234"
    )
    
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="需求分析标题"
    )
    
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="需求简要描述"
    )
    
    # 需求文档信息
    document_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
        comment="原始需求文档 URL（MinIO）"
    )
    
    document_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="文档类型（PDF, Word, etc.）"
    )
    
    # AI 分析结果
    executive_summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="需求概述（Executive Summary）"
    )
    
    functional_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="功能需求分析"
    )
    
    non_functional_requirements: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="非功能需求分析"
    )
    
    user_stories: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="用户故事列表"
    )
    
    acceptance_criteria: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="验收标准列表"
    )
    
    dependencies: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="依赖关系"
    )
    
    risks: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="风险评估"
    )
    
    recommendations: Mapped[list | None] = mapped_column(
        JSONB,
        nullable=True,
        default=list,
        comment="建议和改进意见"
    )
    
    # 优先级分析
    priority_analysis: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="优先级分析（各功能的优先级评估）"
    )
    
    # 工作量评估
    effort_estimation: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="工作量评估（开发、测试工时等）"
    )
    
    # 质量评分
    quality_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="需求文档质量评分（0-100）"
    )
    
    completeness_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="完整性评分（0-100）"
    )
    
    clarity_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="清晰度评分（0-100）"
    )
    
    consistency_score: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="一致性评分（0-100）"
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
    status: Mapped[RequirementAnalysisStatus] = mapped_column(
        SQLEnum(RequirementAnalysisStatus),
        default=RequirementAnalysisStatus.DRAFT,
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
    project: Mapped["Project"] = relationship("Project", back_populates="requirement_analyses")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by])
    owner: Mapped["User | None"] = relationship(
        "User", foreign_keys=[owner_id]
    )
    
    def __repr__(self) -> str:
        return f"<RequirementAnalysis(id={self.id}, identifier={self.identifier}, title={self.title})>"

