"""
UI自动化测试报告数据对象(DO - Data Object)
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from config.database import Base


class UITestReport(Base):
    """UI自动化测试报告表"""
    __tablename__ = 'ui_test_report'
    __table_args__ = {'comment': 'UI自动化测试报告表'}
    
    report_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,
        comment='报告ID'
    )
    execution_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment='执行ID'
    )
    report_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment='报告名称'
    )
    report_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment='报告类型：html/json/playwright'
    )
    report_path: Mapped[Optional[str]] = mapped_column(
        String(500),
        nullable=True,
        comment='存储路径'
    )
    report_size: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True,
        comment='报告大小（字节）'
    )
    summary: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='报告摘要'
    )
    metrics: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment='关键指标'
    )
    create_time: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        default=datetime.now,
        comment='创建时间'
    )

