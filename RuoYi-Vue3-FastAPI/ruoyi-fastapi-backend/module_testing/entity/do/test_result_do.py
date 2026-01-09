"""
测试结果数据对象

记录每次测试执行的结果
参照 ai-test-management 项目的设计
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, JSON, Float, ForeignKey
import enum

from config.database import Base


class TestResultStatus(str, enum.Enum):
    """测试结果状态"""
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"
    RETEST = "retest"


class TestResultDO(Base):
    """测试结果表"""
    __tablename__ = 'test_result'
    __table_args__ = (
        Index('idx_result_case_id', 'case_id'),
        Index('idx_result_plan_id', 'plan_id'),
        Index('idx_result_run_id', 'run_id'),
        Index('idx_result_status', 'status'),
        Index('idx_result_executed_at', 'executed_at'),
        {'comment': '测试结果表'}
    )

    # 主键
    result_id = Column(Integer, primary_key=True, autoincrement=True, comment='结果ID')
    
    # 关联字段
    case_id = Column(Integer, nullable=False, comment='测试用例ID')
    plan_id = Column(Integer, comment='测试计划ID')
    run_id = Column(Integer, comment='测试运行ID')
    project_id = Column(Integer, nullable=False, comment='项目ID')
    
    # 结果信息
    status = Column(
        String(20),
        default=TestResultStatus.PENDING.value,
        comment='状态(pending/passed/failed/blocked/skipped/retest)'
    )
    
    # 执行信息
    executed_by = Column(String(100), comment='执行人')
    executed_at = Column(DateTime, comment='执行时间')
    duration = Column(Float, default=0, comment='执行时长(秒)')
    
    # 步骤结果
    step_results = Column(JSON, comment='步骤执行结果列表')
    
    # 缺陷关联
    defect_ids = Column(JSON, comment='关联的缺陷ID列表')
    
    # 附件
    attachments = Column(JSON, comment='附件列表(截图、日志等)')
    
    # 备注
    comment = Column(Text, comment='执行备注')
    actual_result = Column(Text, comment='实际结果')
    
    # 环境信息
    environment = Column(String(200), comment='执行环境')
    browser = Column(String(100), comment='浏览器')
    device = Column(String(100), comment='设备')
    
    # 自动化执行信息
    is_automated = Column(Integer, default=0, comment='是否自动化执行')
    automation_log = Column(Text, comment='自动化执行日志')
    
    # 版本控制
    version = Column(Integer, default=1, comment='版本号')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'result_id': self.result_id,
            'case_id': self.case_id,
            'plan_id': self.plan_id,
            'run_id': self.run_id,
            'project_id': self.project_id,
            'status': self.status,
            'executed_by': self.executed_by,
            'executed_at': self.executed_at.strftime('%Y-%m-%d %H:%M:%S') if self.executed_at else None,
            'duration': self.duration,
            'step_results': self.step_results or [],
            'defect_ids': self.defect_ids or [],
            'attachments': self.attachments or [],
            'comment': self.comment,
            'actual_result': self.actual_result,
            'environment': self.environment,
            'browser': self.browser,
            'device': self.device,
            'is_automated': bool(self.is_automated),
            'automation_log': self.automation_log,
            'version': self.version,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

    def __repr__(self):
        return f"<TestResultDO(result_id={self.result_id}, case_id={self.case_id}, status='{self.status}')>"


class TestRunDO(Base):
    """测试运行表（一次测试执行）"""
    __tablename__ = 'test_run'
    __table_args__ = (
        Index('idx_run_plan_id', 'plan_id'),
        Index('idx_run_project_id', 'project_id'),
        Index('idx_run_status', 'status'),
        {'comment': '测试运行表'}
    )

    # 主键
    run_id = Column(Integer, primary_key=True, autoincrement=True, comment='运行ID')
    
    # 标识符
    identifier = Column(String(50), unique=True, comment='运行标识符(如 TR-001)')
    
    # 关联字段
    plan_id = Column(Integer, comment='测试计划ID')
    project_id = Column(Integer, nullable=False, comment='项目ID')
    
    # 基本信息
    name = Column(String(200), nullable=False, comment='运行名称')
    description = Column(Text, comment='运行描述')
    
    # 状态
    status = Column(String(20), default='pending', comment='状态(pending/running/completed/aborted)')
    
    # 执行信息
    assigned_to = Column(String(100), comment='分配给')
    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')
    
    # 统计
    total_cases = Column(Integer, default=0, comment='总用例数')
    passed = Column(Integer, default=0, comment='通过数')
    failed = Column(Integer, default=0, comment='失败数')
    blocked = Column(Integer, default=0, comment='阻塞数')
    skipped = Column(Integer, default=0, comment='跳过数')
    
    # 环境配置
    environment = Column(String(200), comment='测试环境')
    build_version = Column(String(100), comment='构建版本')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'run_id': self.run_id,
            'identifier': self.identifier,
            'plan_id': self.plan_id,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'status': self.status,
            'assigned_to': self.assigned_to,
            'started_at': self.started_at.strftime('%Y-%m-%d %H:%M:%S') if self.started_at else None,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M:%S') if self.completed_at else None,
            'total_cases': self.total_cases,
            'passed': self.passed,
            'failed': self.failed,
            'blocked': self.blocked,
            'skipped': self.skipped,
            'environment': self.environment,
            'build_version': self.build_version,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None
        }

