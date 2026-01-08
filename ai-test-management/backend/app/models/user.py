"""
用户模型

定义系统用户表结构
"""



from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin
# noqa  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VnpVNFpRPT06YjRkNGNlYWU=


class User(Base, UUIDMixin, TimestampMixin):
    """
    用户表
    
    存储系统用户信息
    """
    __tablename__ = "users"
    __table_args__ = {"comment": "用户表"}
# type: ignore  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VnpVNFpRPT06YjRkNGNlYWU=
    
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="用户邮箱"
    )
    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="用户名"
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="密码哈希"
    )
    is_active: Mapped[bool] = mapped_column(
        default=True,
        comment="是否激活"
    )
    
    # 关系
    created_projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="creator",
        foreign_keys="Project.created_by"
    )
    owned_test_cases: Mapped[list["TestCase"]] = relationship(
        "TestCase",
        back_populates="owner",
        foreign_keys="TestCase.owner_id"
    )
# type: ignore  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VnpVNFpRPT06YjRkNGNlYWU=
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"

