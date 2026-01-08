"""
SQLAlchemy 数据库模型模块

定义所有 PostgreSQL 数据库表的 ORM 模型
"""



from .base import Base, TimestampMixin, UUIDMixin
from .user import User
from .team import Team, ProjectTeam
from .project import Project
from .folder import Folder
from .test_case import TestCase, TestStep, Tag, TestCaseTag
from .test_run import TestRun, TestRunTestCase
from .test_result import TestResult, TestStepResult
from .attachment import Attachment, AttachmentEntityType
from .configuration import Configuration
from .test_plan import TestPlan
# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmtRMFNBPT06NDIxMDg0YTA=

# 枚举类型从 schemas.enums 导入，避免重复定义
from ..schemas.enums import TestPlanStatus, TestPlanActiveState
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WmtRMFNBPT06NDIxMDg0YTA=

__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDMixin",
    "User",
    "Team",
    "ProjectTeam",
    "Project",
    "Folder",
    "TestCase",
    "TestStep",
    "Tag",
    "TestCaseTag",
    "TestRun",
    "TestRunTestCase",
    "TestResult",
    "TestStepResult",
    "Attachment",
    "AttachmentEntityType",
    "Configuration",
    "TestPlan",
    "TestPlanStatus",
    "TestPlanActiveState",
]

