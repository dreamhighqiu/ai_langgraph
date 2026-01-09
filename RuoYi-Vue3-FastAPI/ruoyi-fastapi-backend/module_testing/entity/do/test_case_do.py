"""
测试用例数据对象
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

from config.database import Base
from common.constant import CommonConstant


class TestCaseDO(Base):
    """测试用例表"""
    __tablename__ = 'test_case'
    __table_args__ = (
        Index('idx_project_id', 'project_id'),
        Index('idx_folder_id', 'folder_id'),
        Index('idx_status', 'status'),
        Index('idx_create_time', 'create_time'),
        {'comment': '测试用例表'}
    )

    # 主键
    case_id = Column(Integer, primary_key=True, autoincrement=True, comment='测试用例ID')
    
    # 关联字段
    project_id = Column(Integer, nullable=False, comment='项目ID')
    folder_id = Column(Integer, comment='文件夹ID')
    
    # 基本信息
    case_identifier = Column(String(100), unique=True, nullable=False, comment='用例标识符(TC-001)')
    case_name = Column(String(200), nullable=False, comment='用例名称')
    case_type = Column(String(50), comment='用例类型(functional/regression/smoke)')
    template = Column(String(50), default='test_case', comment='模板类型(test_case/test_case_bdd)')
    
    # 详细信息
    description = Column(Text, comment='用例描述')
    preconditions = Column(Text, comment='前置条件')
    test_data = Column(Text, comment='测试数据')
    expected_results = Column(Text, comment='预期结果')
    
    # 步骤信息(JSON格式)
    test_case_steps = Column(Text, comment='测试步骤(JSON数组)')
    
    # BDD字段
    feature = Column(Text, comment='BDD Feature')
    scenario = Column(Text, comment='BDD Scenario')
    background = Column(Text, comment='BDD Background')
    given_steps = Column(Text, comment='BDD Given步骤(JSON)')
    when_steps = Column(Text, comment='BDD When步骤(JSON)')
    then_steps = Column(Text, comment='BDD Then步骤(JSON)')
    
    # 属性字段
    priority = Column(String(20), default='medium', comment='优先级(critical/high/medium/low)')
    severity = Column(String(20), comment='严重程度')
    tags = Column(String(500), comment='标签(逗号分隔)')
    
    # 关联信息
    linked_requirements = Column(Text, comment='关联需求(JSON)')
    linked_defects = Column(Text, comment='关联缺陷(JSON)')
    
    # 附件信息
    attachments = Column(Text, comment='附件信息(JSON)')
    
    # 状态字段
    status = Column(String(20), default='draft', comment='状态(draft/active/deprecated)')
    execution_status = Column(String(20), comment='执行状态(not_run/passed/failed/blocked)')
    
    # 统计字段
    execution_count = Column(Integer, default=0, comment='执行次数')
    pass_count = Column(Integer, default=0, comment='通过次数')
    fail_count = Column(Integer, default=0, comment='失败次数')
    
    # 审计字段
    create_by = Column(String(64), default='', comment='创建者')
    create_time = Column(DateTime, default=datetime.now, comment='创建时间')
    update_by = Column(String(64), default='', comment='更新者')
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    remark = Column(String(500), default='', comment='备注')
    
    def to_dict(self):
        """转换为字典"""
        import json
        return {
            'case_id': self.case_id,
            'project_id': self.project_id,
            'folder_id': self.folder_id,
            'case_identifier': self.case_identifier,
            'case_name': self.case_name,
            'case_type': self.case_type,
            'template': self.template,
            'description': self.description,
            'preconditions': self.preconditions,
            'test_data': self.test_data,
            'expected_results': self.expected_results,
            'test_case_steps': json.loads(self.test_case_steps) if self.test_case_steps else [],
            'feature': self.feature,
            'scenario': self.scenario,
            'background': self.background,
            'given_steps': json.loads(self.given_steps) if self.given_steps else [],
            'when_steps': json.loads(self.when_steps) if self.when_steps else [],
            'then_steps': json.loads(self.then_steps) if self.then_steps else [],
            'priority': self.priority,
            'severity': self.severity,
            'tags': self.tags.split(',') if self.tags else [],
            'linked_requirements': json.loads(self.linked_requirements) if self.linked_requirements else [],
            'linked_defects': json.loads(self.linked_defects) if self.linked_defects else [],
            'attachments': json.loads(self.attachments) if self.attachments else [],
            'status': self.status,
            'execution_status': self.execution_status,
            'execution_count': self.execution_count,
            'pass_count': self.pass_count,
            'fail_count': self.fail_count,
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'remark': self.remark
        }

