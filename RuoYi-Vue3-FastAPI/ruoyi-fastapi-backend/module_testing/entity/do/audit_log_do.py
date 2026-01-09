"""
审计日志数据对象

记录所有重要操作的审计日志
支持版本控制和变更追踪
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, JSON

from config.database import Base


class AuditLogDO(Base):
    """审计日志表"""
    __tablename__ = 'test_audit_log'
    __table_args__ = (
        Index('idx_audit_entity_type', 'entity_type'),
        Index('idx_audit_entity_id', 'entity_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_user_id', 'user_id'),
        Index('idx_audit_created_at', 'created_at'),
        {'comment': '审计日志表'}
    )

    # 主键
    log_id = Column(Integer, primary_key=True, autoincrement=True, comment='日志ID')
    
    # 实体信息
    entity_type = Column(String(50), nullable=False, comment='实体类型(test_case/test_plan/project等)')
    entity_id = Column(Integer, nullable=False, comment='实体ID')
    entity_identifier = Column(String(100), comment='实体标识符')
    
    # 操作信息
    action = Column(String(50), nullable=False, comment='操作类型(create/update/delete/execute等)')
    action_desc = Column(String(200), comment='操作描述')
    
    # 变更内容
    old_value = Column(JSON, comment='变更前的值')
    new_value = Column(JSON, comment='变更后的值')
    diff = Column(JSON, comment='差异详情')
    
    # 操作人
    user_id = Column(Integer, comment='操作人ID')
    user_name = Column(String(100), comment='操作人姓名')
    
    # 来源信息
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(500), comment='用户代理')
    
    # 关联项目
    project_id = Column(Integer, comment='项目ID')
    
    # 时间
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'log_id': self.log_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'entity_identifier': self.entity_identifier,
            'action': self.action,
            'action_desc': self.action_desc,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'diff': self.diff,
            'user_id': self.user_id,
            'user_name': self.user_name,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'project_id': self.project_id,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

    def __repr__(self):
        return f"<AuditLogDO(log_id={self.log_id}, entity_type='{self.entity_type}', action='{self.action}')>"


class VersionHistoryDO(Base):
    """版本历史表（保存实体的历史版本）"""
    __tablename__ = 'test_version_history'
    __table_args__ = (
        Index('idx_version_entity_type', 'entity_type'),
        Index('idx_version_entity_id', 'entity_id'),
        Index('idx_version_number', 'version_number'),
        {'comment': '版本历史表'}
    )

    # 主键
    history_id = Column(Integer, primary_key=True, autoincrement=True, comment='历史ID')
    
    # 实体信息
    entity_type = Column(String(50), nullable=False, comment='实体类型')
    entity_id = Column(Integer, nullable=False, comment='实体ID')
    
    # 版本信息
    version_number = Column(Integer, nullable=False, comment='版本号')
    
    # 快照
    snapshot = Column(JSON, nullable=False, comment='实体快照')
    
    # 变更描述
    change_summary = Column(String(500), comment='变更摘要')
    change_details = Column(JSON, comment='变更详情')
    
    # 操作人
    created_by = Column(String(100), comment='创建人')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    def to_dict(self):
        """转换为字典"""
        return {
            'history_id': self.history_id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'version_number': self.version_number,
            'snapshot': self.snapshot,
            'change_summary': self.change_summary,
            'change_details': self.change_details,
            'created_by': self.created_by,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }

