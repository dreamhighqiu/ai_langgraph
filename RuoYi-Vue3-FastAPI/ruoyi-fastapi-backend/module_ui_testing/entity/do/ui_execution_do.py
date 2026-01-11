"""
UI自动化测试执行记录数据对象(DO - Data Object)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class UITestExecution(Base):
    """UI自动化测试执行记录表"""
    __tablename__ = 'ui_test_execution'
    __table_args__ = {'comment': 'UI自动化测试执行记录表'}
    
    execution_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='执行ID'
    )
    script_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='脚本ID'
    )
    execution_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='manual',
        comment='执行类型：manual/scheduled/ci'
    )
    execution_status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='pending',
        comment='执行状态：pending/running/success/failed/cancelled'
    )
    browser: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default='chromium',
        comment='执行浏览器：chromium/firefox/webkit'
    )
    headless: Mapped[str] = mapped_column(
        String(1),
        nullable=False,
        default='1',
        comment='是否无头模式（0否 1是）'
    )
    start_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='开始时间'
    )
    end_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        comment='结束时间'
    )
    duration: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment='执行时长（秒）'
    )
    thread_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='LangGraph线程ID'
    )
    agent_id: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
        comment='Agent ID'
    )
    config: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='执行配置'
    )
    result: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='执行结果'
    )
    error_msg: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment='错误信息'
    )
    executor: Mapped[Optional[str]] = mapped_column(
        String(64),
        nullable=True,
        comment='执行者'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment='创建时间'
    )
    update_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        onupdate=datetime.now,
        comment='更新时间'
    )

