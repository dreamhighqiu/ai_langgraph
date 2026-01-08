"""
项目模型

定义项目表结构
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVhscll3PT06ZDJhZjBhYzA=

from app.models.base import Base, TimestampMixin, UUIDMixin
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVhscll3PT06ZDJhZjBhYzA=


class Project(Base, UUIDMixin, TimestampMixin):
    """
    项目表
    
    存储测试项目信息
    """
    __tablename__ = "projects"
    __table_args__ = {"comment": "项目表"}
    
    identifier: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="项目标识符，如 PR-1234"
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="项目名称"
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="项目描述"
    )
    created_by: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
        comment="创建者 ID"
    )
# fmt: off  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVhscll3PT06ZDJhZjBhYzA=
    
    # 关系
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_projects",
        foreign_keys=[created_by]
    )
    teams: Mapped[list["Team"]] = relationship(
        "Team",
        secondary="project_teams",
        back_populates="projects"
    )
    folders: Mapped[list["Folder"]] = relationship(
        "Folder",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    test_cases: Mapped[list["TestCase"]] = relationship(
        "TestCase",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    test_runs: Mapped[list["TestRun"]] = relationship(
        "TestRun",
        back_populates="project",
        cascade="all, delete-orphan"
    )
    test_plans: Mapped[list["TestPlan"]] = relationship(
        "TestPlan",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, identifier={self.identifier}, name={self.name})>"

# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VVhscll3PT06ZDJhZjBhYzA=
