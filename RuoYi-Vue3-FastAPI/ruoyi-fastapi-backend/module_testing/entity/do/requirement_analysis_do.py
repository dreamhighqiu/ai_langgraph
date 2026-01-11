"""
需求分析数据对象 (MySQL: test_requirement_analysis)

注意：本 DO 需与 Alembic `add_testing_tables_mysql.py` / `sql/testing_module_full.sql`
中 `test_requirement_analysis` 表结构保持一致。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from config.database import Base


class RequirementAnalysisDO(Base):
    """需求分析表"""

    __tablename__ = "test_requirement_analysis"
    __table_args__ = (
        Index("idx_req_project_id", "project_id"),
        Index("idx_req_status", "status"),
        Index("idx_req_priority", "priority"),
        Index("idx_req_create_time", "create_time"),
        {"comment": "需求分析表"},
    )

    requirement_id = Column(Integer, primary_key=True, autoincrement=True, comment="需求ID")
    project_id = Column(Integer, nullable=False, comment="项目ID")
    knowledge_id = Column(Integer, comment="关联知识库ID")

    requirement_identifier = Column(String(50), comment="需求标识")
    requirement_name = Column(String(200), nullable=False, comment="需求名称")
    requirement_type = Column(String(50), default="functional", comment="需求类型")
    priority = Column(String(20), default="medium", comment="优先级")
    module = Column(String(200), comment="所属模块")

    description = Column(Text, comment="需求描述")
    acceptance_criteria = Column(Text, comment="验收标准")
    functional_requirements = Column(Text, comment="功能需求")
    non_functional_requirements = Column(Text, comment="非功能需求")
    business_rules = Column(Text, comment="业务规则")
    dependencies = Column(Text, comment="依赖关系(JSON)")
    stakeholders = Column(Text, comment="干系人(JSON)")

    use_rag = Column(Integer, default=0, comment="是否使用RAG(0否1是)")
    rag_context = Column(Text, comment="RAG检索上下文")

    status = Column(String(20), default="draft", comment="状态(draft/pending/approved/rejected)")
    tags = Column(String(500), comment="标签(逗号分隔)")

    report_url = Column(String(500), comment="分析报告URL")

    create_by = Column(String(64), default="", comment="创建者")
    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_by = Column(String(64), default="", comment="更新者")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    remark = Column(String(500), default="", comment="备注")

    def to_dict(self) -> dict:
        return {
            "requirement_id": self.requirement_id,
            "project_id": self.project_id,
            "knowledge_id": self.knowledge_id,
            "requirement_identifier": self.requirement_identifier,
            "requirement_name": self.requirement_name,
            "requirement_type": self.requirement_type,
            "priority": self.priority,
            "module": self.module,
            "description": self.description,
            "acceptance_criteria": self.acceptance_criteria,
            "functional_requirements": self.functional_requirements,
            "non_functional_requirements": self.non_functional_requirements,
            "business_rules": self.business_rules,
            "dependencies": self.dependencies,
            "stakeholders": self.stakeholders,
            "use_rag": self.use_rag,
            "rag_context": self.rag_context,
            "status": self.status,
            "tags": self.tags,
            "report_url": self.report_url,
            "create_by": self.create_by,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_by": self.update_by,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
            "remark": self.remark,
        }

    # ========= Backward-compatible aliases (historical code paths) =========

    @property
    def analysis_id(self) -> int:
        return self.requirement_id

    @property
    def analysis_name(self) -> str:
        return self.requirement_name

    @property
    def executive_summary(self) -> str | None:
        return self.description
