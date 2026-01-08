"""
附件模型

定义附件的表结构
参考: https://www.browserstack.com/docs/test-management/api-reference/attachments
"""



from enum import Enum as PyEnum

from sqlalchemy import ForeignKey, Integer, String, Text, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ROU01RPT06MGRkYjIwMGM=

from app.models.base import Base, TimestampMixin, UUIDMixin


class AttachmentEntityType(str, PyEnum):
    """附件关联的实体类型"""
    TEST_CASE = "test_case"
    TEST_CASE_STEP = "test_case_step"
    TEST_RESULT = "test_result"
    TEST_STEP_RESULT = "test_step_result"


class Attachment(Base, UUIDMixin, TimestampMixin):
    """
    附件表

    存储上传的附件元数据，实际文件存储在 MinIO
    """
    __tablename__ = "attachments"
    __table_args__ = {"comment": "附件表"}
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ROU01RPT06MGRkYjIwMGM=

    # 关联实体类型和 ID
    entity_type: Mapped[AttachmentEntityType] = mapped_column(
        SQLEnum(AttachmentEntityType),
        nullable=False,
        index=True,
        comment="关联实体类型"
    )
    entity_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        index=True,
        comment="关联实体 ID"
    )
    
    # 项目关联（用于权限控制）
    project_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="项目 ID"
    )
    
    # 文件信息
    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        comment="原始文件名"
    )
    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="文件大小（字节）"
    )
    content_type: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="MIME 类型"
    )
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ROU01RPT06MGRkYjIwMGM=
    
    # MinIO 存储信息
    object_name: Mapped[str] = mapped_column(
        String(1000),
        nullable=False,
        unique=True,
        comment="MinIO 对象名称"
    )
    
    # 额外信息
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="附件描述"
    )
    created_by: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="上传人邮箱"
    )
    
    # 步骤相关（当 entity_type 为 test_case_step 或 test_step_result 时）
    step_index: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="步骤索引（从 1 开始）"
    )
# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V1ROU01RPT06MGRkYjIwMGM=

    # 关系
    project: Mapped["Project"] = relationship(
        "Project",
        backref="attachments"
    )

    def __repr__(self) -> str:
        return f"<Attachment(id={self.id}, file_name={self.file_name})>"

