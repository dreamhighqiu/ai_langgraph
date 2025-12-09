from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.types import JSON

LegacyBase = declarative_base()


class ProjectLegacy(LegacyBase):
    __tablename__ = "project"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    desc = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class OriginalRequirementLegacy(LegacyBase):
    __tablename__ = "original_requirements"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    markdown_content = Column(Text)
    status = Column(String(50), default="未处理")
    remark = Column(Text)
    minio_bucket = Column(String(100))
    knowledge_base = Column(String(100))
    file_ids = Column(JSON)
    analysis_content = Column(Text)
    requirement_report = Column(Text)
    json_content = Column(Text)
    testcase_content = Column(Text)
    review_report = Column(Text)
    finalize_result = Column(Text)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class RequirementLegacy(LegacyBase):
    __tablename__ = "requirements"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(20), nullable=True)
    parent = Column(String(50))
    module = Column(String(50))
    level = Column(String(20))
    reviewer = Column(String(50))
    keywords = Column(String(100))
    estimate = Column(Integer)
    criteria = Column(Text)
    remark = Column(Text)
    testcase_content = Column(Text)
    review_report = Column(Text)
    finalize_result = Column(Text)
    original_requirement_name = Column(String(255))
    requirements_count = Column(Integer, default=0)
    testcases_count = Column(Integer, default=0)
    project_id = Column(Integer, ForeignKey("project.id"), nullable=True)
    original_requirement_id = Column(
        Integer, ForeignKey("original_requirements.id"), nullable=True
    )
    status = Column(String(50))
    priority = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestCaseLegacy(LegacyBase):
    __tablename__ = "test_cases"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    case_id = Column(String(50))
    module = Column(String(100))
    feature = Column(String(100))
    desc = Column(Text)
    priority = Column(String(20))
    status = Column(String(20))
    tags = Column(String(255))
    preconditions = Column(Text)
    postconditions = Column(Text)
    actual_result = Column(Text)
    remark = Column(Text)
    project_id = Column(Integer, ForeignKey("project.id"))
    requirement_id = Column(Integer, ForeignKey("requirements.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestStepLegacy(LegacyBase):
    __tablename__ = "test_steps"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    description = Column(Text)
    expected_result = Column(Text)
    order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TestCaseReviewLegacy(LegacyBase):
    __tablename__ = "testcase_reviews"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    issues = Column(JSON)
    score = Column(Integer)
    next_steps = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)


class TestExecutionLegacy(LegacyBase):
    __tablename__ = "test_executions"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    name = Column(String(255))
    status = Column(String(50))
    result = Column(Text)
    report_url = Column(String(500))
    log_url = Column(String(500))
    metadata_payload = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ReportLegacy(LegacyBase):
    __tablename__ = "reports"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(Integer, ForeignKey("agent_runs.id"), nullable=False)
    title = Column(String(255))
    summary = Column(Text)
    url = Column(String(500))
    type = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
