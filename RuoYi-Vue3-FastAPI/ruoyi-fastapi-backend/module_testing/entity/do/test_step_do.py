"""
测试步骤数据对象

独立的测试步骤表，便于管理和查询
参照 ai-test-management 项目的设计
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base


class TestStepDO(Base):
    """测试步骤表"""
    __tablename__ = 'test_case_step'
    __table_args__ = (
        Index('idx_case_id', 'case_id'),
        Index('idx_step_number', 'step_number'),
        {'comment': '测试用例步骤表'}
    )

    # 主键
    step_id = Column(Integer, primary_key=True, autoincrement=True, comment='步骤ID')
    
    # 关联字段
    case_id = Column(
        Integer, 
        ForeignKey('test_case.case_id', ondelete='CASCADE'),
        nullable=False, 
        comment='测试用例ID'
    )
    
    # 步骤信息
    step_number = Column(Integer, nullable=False, comment='步骤序号')
    action = Column(Text, nullable=False, comment='操作步骤描述')
    expected_result = Column(Text, comment='预期结果')
    actual_result = Column(Text, comment='实际结果（执行时填写）')
    
    # 步骤状态
    status = Column(String(20), default='pending', comment='步骤状态(pending/passed/failed/blocked)')
    
    # BDD 步骤类型（可选）
    step_type = Column(String(20), comment='BDD步骤类型(given/when/then/and/but)')
    
    # 附加数据
    test_data = Column(Text, comment='测试数据')
    screenshot = Column(String(500), comment='截图路径')
    notes = Column(Text, comment='备注')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'step_id': self.step_id,
            'case_id': self.case_id,
            'step_number': self.step_number,
            'action': self.action,
            'expected_result': self.expected_result,
            'actual_result': self.actual_result,
            'status': self.status,
            'step_type': self.step_type,
            'test_data': self.test_data,
            'screenshot': self.screenshot,
            'notes': self.notes,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
        }
    
    def __repr__(self):
        return f"<TestStepDO(step_id={self.step_id}, case_id={self.case_id}, step_number={self.step_number})>"

