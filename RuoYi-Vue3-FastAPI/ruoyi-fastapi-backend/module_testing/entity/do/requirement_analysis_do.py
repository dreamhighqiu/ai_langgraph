"""
需求分析数据对象
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index, Float

from config.database import Base


class RequirementAnalysisDO(Base):
    """需求分析表"""
    __tablename__ = 'test_requirement_analysis'
    __table_args__ = (
        Index('idx_project_id', 'project_id'),
        Index('idx_status', 'status'),
        Index('idx_create_time', 'create_time'),
        {'comment': '需求分析表'}
    )

    # 主键
    analysis_id = Column(Integer, primary_key=True, autoincrement=True, comment='分析ID')
    
    # 关联字段
    project_id = Column(Integer, nullable=False, comment='项目ID')
    knowledge_id = Column(Integer, comment='关联知识库ID')
    
    # 基本信息
    analysis_name = Column(String(200), nullable=False, comment='分析名称')
    document_name = Column(String(200), comment='文档名称')
    document_path = Column(String(500), comment='文档路径')
    
    # 分析结果
    executive_summary = Column(Text, comment='需求概述')
    functional_requirements = Column(Text, comment='功能需求分析(JSON)')
    non_functional_requirements = Column(Text, comment='非功能需求分析(JSON)')
    user_stories = Column(Text, comment='用户故事(JSON数组)')
    acceptance_criteria = Column(Text, comment='验收标准(JSON)')
    dependencies = Column(Text, comment='依赖关系(JSON)')
    risks = Column(Text, comment='风险评估(JSON)')
    recommendations = Column(Text, comment='改进建议(JSON)')
    
    # 质量评分
    quality_completeness = Column(Float, comment='完整性评分(0-100)')
    quality_clarity = Column(Float, comment='清晰度评分(0-100)')
    quality_consistency = Column(Float, comment='一致性评分(0-100)')
    quality_testability = Column(Float, comment='可测试性评分(0-100)')
    quality_overall = Column(Float, comment='总体评分(0-100)')
    
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
            'analysis_name': self.analysis_name,
            'document_name': self.document_name,
            'document_path': self.document_path,
            'executive_summary': self.executive_summary,
            'functional_requirements': json.loads(self.functional_requirements) if self.functional_requirements else {},
            'non_functional_requirements': json.loads(self.non_functional_requirements) if self.non_functional_requirements else {},
            'user_stories': json.loads(self.user_stories) if self.user_stories else [],
            'acceptance_criteria': json.loads(self.acceptance_criteria) if self.acceptance_criteria else {},
            'dependencies': json.loads(self.dependencies) if self.dependencies else [],
            'risks': json.loads(self.risks) if self.risks else [],
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'quality_completeness': self.quality_completeness,
            'quality_clarity': self.quality_clarity,
            'quality_consistency': self.quality_consistency,
            'quality_testability': self.quality_testability,
            'quality_overall': self.quality_overall,
            'use_rag': self.use_rag,
            'rag_context': self.rag_context,
            'mindmap_data': json.loads(self.mindmap_data) if self.mindmap_data else {},
            'mindmap_url': self.mindmap_url,
            'report_url': self.report_url,
            'status': self.status,
            'process_status': self.process_status,
            'error_message': self.error_message,
            'tags': self.tags.split(',') if self.tags else [],
            'create_by': self.create_by,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_by': self.update_by,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
            'remark': self.remark
        }

