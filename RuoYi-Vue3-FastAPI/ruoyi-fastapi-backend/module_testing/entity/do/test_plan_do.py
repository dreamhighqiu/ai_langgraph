"""
测试计划数据对象

参照 ai-test-management 项目的设计
"""
from datetime import datetime, date
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, Index, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from config.database import Base


class TestPlanStatus(str, enum.Enum):
    """测试计划状态"""
    DRAFT = "draft"
    READY = "ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class TestPlanDO(Base):
    """测试计划表"""
    __tablename__ = 'test_plan'
    __table_args__ = (
        Index('idx_plan_project_id', 'project_id'),
        Index('idx_plan_status', 'status'),
        Index('idx_plan_start_date', 'start_date'),
        {'comment': '测试计划表'}
    )

    # 主键
    plan_id = Column(Integer, primary_key=True, autoincrement=True, comment='测试计划ID')
    
    # 标识符
    identifier = Column(String(50), unique=True, comment='计划标识符(如 TP-001)')
    
    # 关联字段
    project_id = Column(Integer, nullable=False, comment='项目ID')
    
    # 基本信息
    name = Column(String(200), nullable=False, comment='计划名称')
    description = Column(Text, comment='计划描述')
    
    # 测试范围
    scope = Column(Text, comment='测试范围')
    objectives = Column(Text, comment='测试目标')
    
    # 时间安排
    start_date = Column(Date, comment='开始日期')
    end_date = Column(Date, comment='结束日期')
    
    # 状态
    status = Column(
        String(20),
        default=TestPlanStatus.DRAFT.value,
        comment='状态(draft/ready/in_progress/completed/archived)'
    )
    
    # 资源分配
    owner = Column(String(100), comment='负责人')
    testers = Column(JSON, comment='测试人员列表')
    
    # 环境配置
    test_environment = Column(Text, comment='测试环境描述')
    test_data_requirements = Column(Text, comment='测试数据需求')
    
    # 入口/出口标准
    entry_criteria = Column(Text, comment='入口标准')
    exit_criteria = Column(Text, comment='出口标准')
    
    # 风险和缓解
    risks = Column(JSON, comment='风险列表')
    mitigations = Column(JSON, comment='缓解措施')
    
    # 统计信息
    total_cases = Column(Integer, default=0, comment='总用例数')
    executed_cases = Column(Integer, default=0, comment='已执行用例数')
    passed_cases = Column(Integer, default=0, comment='通过用例数')
    failed_cases = Column(Integer, default=0, comment='失败用例数')
    blocked_cases = Column(Integer, default=0, comment='阻塞用例数')
    
    # 进度
    progress = Column(Integer, default=0, comment='进度百分比')
    
    # 版本控制
    version = Column(Integer, default=1, comment='版本号(乐观锁)')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), default='', comment='备注')

    def to_dict(self):
        """转换为字典"""
        return {
            'plan_id': self.plan_id,
            'identifier': self.identifier,
            'project_id': self.project_id,
            'name': self.name,
            'description': self.description,
            'scope': self.scope,
            'objectives': self.objectives,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'status': self.status,
            'owner': self.owner,
            'testers': self.testers or [],
            'test_environment': self.test_environment,
            'test_data_requirements': self.test_data_requirements,
            'entry_criteria': self.entry_criteria,
            'exit_criteria': self.exit_criteria,
            'risks': self.risks or [],
            'mitigations': self.mitigations or [],
            'total_cases': self.total_cases,
            'executed_cases': self.executed_cases,
            'passed_cases': self.passed_cases,
            'failed_cases': self.failed_cases,
            'blocked_cases': self.blocked_cases,
            'progress': self.progress,
            'version': self.version,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'remark': self.remark
        }

    def __repr__(self):
        return f"<TestPlanDO(plan_id={self.plan_id}, name='{self.name}')>"

