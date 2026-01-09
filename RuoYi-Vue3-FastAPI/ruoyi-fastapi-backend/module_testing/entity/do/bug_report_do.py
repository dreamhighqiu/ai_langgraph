"""
缺陷报告数据对象
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, Index, Integer, String, Text

from config.database import Base


class BugReportDO(Base):
    """缺陷报告表"""

    __tablename__ = "bug_report"
    __table_args__ = (
        Index("idx_project_id", "project_id"),
        Index("idx_bug_identifier", "bug_identifier"),
        Index("idx_status", "status"),
        {"comment": "缺陷报告表"},
    )

    bug_id = Column(Integer, primary_key=True, autoincrement=True, comment="缺陷ID")

    project_id = Column(Integer, nullable=False, comment="项目ID")
    bug_identifier = Column(String(100), nullable=False, comment="缺陷标识符")
    bug_title = Column(String(200), nullable=False, comment="缺陷标题")
    bug_description = Column(Text, nullable=False, comment="缺陷描述")
    severity = Column(String(20), nullable=False, comment="严重程度")
    priority = Column(String(20), nullable=False, comment="优先级")
    bug_type = Column(String(50), nullable=False, comment="缺陷类型")
    status = Column(String(20), nullable=False, default="open", comment="状态")

    environment = Column(Text, comment="环境信息")
    steps_to_reproduce = Column(Text, comment="复现步骤")
    expected_behavior = Column(Text, comment="预期行为")
    actual_behavior = Column(Text, comment="实际行为")
    attachments = Column(Text, comment="附件")

    reporter = Column(Integer, nullable=False, comment="报告人")
    assigned_to = Column(Integer, comment="分配给")

    create_time = Column(DateTime, default=datetime.now, comment="创建时间")
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment="更新时间")
    resolved_time = Column(DateTime, comment="解决时间")
    remark = Column(String(500), comment="备注")

    def to_dict(self):
        """转换为字典"""
        import json

        def parse_json_maybe(value, default):
            if not value:
                return default
            try:
                return json.loads(value)
            except Exception:
                return value

        return {
            "bug_id": self.bug_id,
            "project_id": self.project_id,
            "bug_identifier": self.bug_identifier,
            "bug_title": self.bug_title,
            "bug_description": self.bug_description,
            "severity": self.severity,
            "priority": self.priority,
            "bug_type": self.bug_type,
            "status": self.status,
            "environment": self.environment,
            "steps_to_reproduce": self.steps_to_reproduce,
            "expected_behavior": self.expected_behavior,
            "actual_behavior": self.actual_behavior,
            "attachments": parse_json_maybe(self.attachments, []),
            "reporter": self.reporter,
            "assigned_to": self.assigned_to,
            "create_time": self.create_time.strftime("%Y-%m-%d %H:%M:%S") if self.create_time else None,
            "update_time": self.update_time.strftime("%Y-%m-%d %H:%M:%S") if self.update_time else None,
            "resolved_time": self.resolved_time.strftime("%Y-%m-%d %H:%M:%S") if self.resolved_time else None,
            "remark": self.remark,
        }

