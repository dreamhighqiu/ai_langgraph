"""
缺陷分析数据对象
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Float

from config.database import Base


class DefectAnalysisDO(Base):
    """缺陷分析表"""
    __tablename__ = 'test_defect_analysis'
    __table_args__ = (
        Index('idx_project_id', 'project_id'),
        Index('idx_severity', 'severity'),
        Index('idx_priority', 'priority'),
        Index('idx_status', 'status'),
        Index('idx_create_time', 'create_time'),
        {'comment': '缺陷分析表'}
    )

    # 主键
    analysis_id = Column(Integer, primary_key=True, autoincrement=True, comment='分析ID')
    
    # 关联字段
    project_id = Column(Integer, nullable=False, comment='项目ID')
    knowledge_id = Column(Integer, comment='关联知识库ID')
    defect_id = Column(String(100), comment='关联缺陷ID')
    
    # 基本信息
    analysis_name = Column(String(200), nullable=False, comment='分析名称')
    defect_title = Column(String(200), comment='缺陷标题')
    defect_description = Column(Text, comment='缺陷描述')
    
    # 分类信息
    severity = Column(String(20), default='medium', comment='严重程度(critical/high/medium/low)')
    priority = Column(String(20), default='medium', comment='优先级(urgent/high/medium/low)')
    defect_type = Column(String(50), comment='缺陷类型(functional/performance/security/ui)')
    category = Column(String(100), comment='详细分类')
    affected_phase = Column(String(50), comment='影响阶段')
    detection_phase = Column(String(50), comment='发现阶段')
    
    # 分析结果
    executive_summary = Column(Text, comment='缺陷概述')
    root_cause_analysis = Column(Text, comment='根本原因分析(JSON)')
    impact_analysis = Column(Text, comment='影响分析(JSON)')
    reproduction_steps = Column(Text, comment='复现步骤(JSON数组)')
    affected_modules = Column(Text, comment='受影响模块(JSON)')
    fix_suggestions = Column(Text, comment='修复建议(JSON)')
    test_suggestions = Column(Text, comment='测试建议(JSON)')
    prevention_measures = Column(Text, comment='预防措施(JSON)')
    similar_defects = Column(Text, comment='相似缺陷(JSON)')
    
    # RAG相关
    use_rag = Column(Integer, default=0, comment='是否使用RAG(0否1是)')
    rag_context = Column(Text, comment='RAG检索上下文')
    
    # 思维导图
    mindmap_data = Column(Text, comment='思维导图数据(JSON)')
    mindmap_url = Column(String(500), comment='思维导图图片URL')
    
    # 报告
    report_url = Column(String(500), comment='分析报告URL')
    
    # 状态字段
    status = Column(String(20), default='draft', comment='状态(draft/analyzing/completed/failed)')
    process_status = Column(String(20), comment='处理状态(pending/processing/completed/failed)')
    error_message = Column(Text, comment='错误信息')
    
    # 修复信息
    fix_status = Column(String(20), comment='修复状态(pending/in_progress/fixed/verified)')
    fix_time_estimate = Column(String(50), comment='预计修复时间')
    actual_fix_time = Column(DateTime, comment='实际修复时间')
    
    # 标签和备注
    tags = Column(String(500), comment='标签(逗号分隔)')
    
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
            'analysis_id': self.analysis_id,
            'project_id': self.project_id,
            'knowledge_id': self.knowledge_id,
            'defect_id': self.defect_id,
            'analysis_name': self.analysis_name,
            'defect_title': self.defect_title,
            'defect_description': self.defect_description,
            'severity': self.severity,
            'priority': self.priority,
            'defect_type': self.defect_type,
            'category': self.category,
            'affected_phase': self.affected_phase,
            'detection_phase': self.detection_phase,
            'executive_summary': self.executive_summary,
            'root_cause_analysis': json.loads(self.root_cause_analysis) if self.root_cause_analysis else {},
            'impact_analysis': json.loads(self.impact_analysis) if self.impact_analysis else {},
            'reproduction_steps': json.loads(self.reproduction_steps) if self.reproduction_steps else [],
            'affected_modules': json.loads(self.affected_modules) if self.affected_modules else [],
            'fix_suggestions': json.loads(self.fix_suggestions) if self.fix_suggestions else [],
            'test_suggestions': json.loads(self.test_suggestions) if self.test_suggestions else [],
            'prevention_measures': json.loads(self.prevention_measures) if self.prevention_measures else [],
            'similar_defects': json.loads(self.similar_defects) if self.similar_defects else [],
            'use_rag': self.use_rag,
            'rag_context': self.rag_context,
            'mindmap_data': json.loads(self.mindmap_data) if self.mindmap_data else {},
            'mindmap_url': self.mindmap_url,
            'report_url': self.report_url,
            'status': self.status,
            'process_status': self.process_status,
            'error_message': self.error_message,
            'fix_status': self.fix_status,
            'fix_time_estimate': self.fix_time_estimate,
            'actual_fix_time': self.actual_fix_time.strftime('%Y-%m-%d %H:%M:%S') if self.actual_fix_time else None,
            'tags': self.tags.split(',') if self.tags else [],
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'remark': self.remark
        }

