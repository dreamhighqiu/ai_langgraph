"""
测试项目数据对象(DO - Data Object)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class TestProject(Base):
    """测试项目表"""
    __tablename__ = 'test_project'
    __table_args__ = {'comment': '测试项目表'}
    
    project_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='项目ID'
    )
    project_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='项目名称'
    )
    project_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default='api',
        comment='项目类型：performance/ui/api'
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='项目描述'
    )
    status: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default='0',
        comment='状态（0正常 1停用）'
    )
    del_flag: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default='0',
        comment='删除标志（0代表存在 2代表删除）'
    )
    create_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='创建者'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment='创建时间'
    )
    update_by: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='更新者'
    )
    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment='更新时间'
    )
    remark: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment='备注'
    )
