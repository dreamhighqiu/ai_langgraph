"""
测试脚本数据对象(DO - Data Object)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class TestScript(Base):
    """测试脚本表"""
    __tablename__ = 'test_script'
    __table_args__ = {'comment': '测试脚本表'}
    
    script_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='脚本ID'
    )
    project_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='项目ID'
    )
    script_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment='脚本名称'
    )
    script_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment='脚本类型：k6/playwright/api'
    )
    script_content: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='脚本内容'
    )
    script_file_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment='MinIO存储路径'
    )
    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='1.0.0',
        comment='版本号'
    )
    config: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='配置参数'
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Agent ID'
    )
    generation_prompt: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='生成提示词'
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
