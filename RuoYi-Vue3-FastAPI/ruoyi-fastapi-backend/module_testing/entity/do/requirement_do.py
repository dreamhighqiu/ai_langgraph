"""
测试需求数据对象(DO - Data Object)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class TestRequirement(Base):
    """测试需求表"""
    __tablename__ = 'test_requirement'
    __table_args__ = {'comment': '测试需求表'}
    
    requirement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='需求ID'
    )
    project_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='项目ID'
    )
    requirement_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment='需求名称'
    )
    requirement_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='需求类型：performance/ui/api'
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='需求描述'
    )
    acceptance_criteria: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='验收标准'
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='medium',
        comment='优先级：low/medium/high'
    )
    status: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default='0',
        comment='状态（0待处理 1进行中 2已完成 3已关闭）'
    )
    tags: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='标签'
    )
    attachments: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='附件'
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

