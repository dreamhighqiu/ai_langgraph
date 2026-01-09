"""Add requirement analysis and defect analysis tables

Revision ID: requirement_defect_001
Revises: test_case_bug_requirement
Create Date: 2025-01-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'requirement_defect_001'
down_revision: Union[str, None] = 'test_case_bug_requirement'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建需求分析状态枚举
    requirement_analysis_status = postgresql.ENUM(
        'draft', 'analyzing', 'completed', 'approved', 'rejected',
        name='requirement_analysis_status',
        create_type=True
    )
    requirement_analysis_status.create(op.get_bind(), checkfirst=True)
    
    # 创建缺陷分析状态枚举
    defect_analysis_status = postgresql.ENUM(
        'draft', 'analyzing', 'completed', 'approved',
        name='defect_analysis_status',
        create_type=True
    )
    defect_analysis_status.create(op.get_bind(), checkfirst=True)
    
    # 创建优先级枚举
    priority_enum = postgresql.ENUM(
        'low', 'medium', 'high', 'critical',
        name='priority',
        create_type=True
    )
    priority_enum.create(op.get_bind(), checkfirst=True)
    
    # 创建需求分析表
    op.create_table(
        'requirement_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('identifier', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('document_url', sa.String(1000), nullable=True),
        sa.Column('document_type', sa.String(100), nullable=True),
        sa.Column('executive_summary', sa.Text, nullable=True),
        sa.Column('functional_requirements', sa.Text, nullable=True),
        sa.Column('non_functional_requirements', sa.Text, nullable=True),
        sa.Column('user_stories', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('acceptance_criteria', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('dependencies', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('risks', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('recommendations', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('priority_analysis', postgresql.JSONB, nullable=True),
        sa.Column('effort_estimation', postgresql.JSONB, nullable=True),
        sa.Column('quality_score', sa.Float, nullable=True),
        sa.Column('completeness_score', sa.Float, nullable=True),
        sa.Column('clarity_score', sa.Float, nullable=True),
        sa.Column('consistency_score', sa.Float, nullable=True),
        sa.Column('rag_context', postgresql.JSONB, nullable=True),
        sa.Column('used_rag', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('status', requirement_analysis_status, nullable=False, server_default='draft'),
        sa.Column('tags', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('custom_fields', postgresql.JSONB, nullable=True, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by'], ['sys_user.user_id']),
        sa.ForeignKeyConstraint(['owner_id'], ['sys_user.user_id'], ondelete='SET NULL'),
        comment='需求分析表'
    )
    
    # 创建索引
    op.create_index('ix_requirement_analyses_project_id', 'requirement_analyses', ['project_id'])
    op.create_index('ix_requirement_analyses_identifier', 'requirement_analyses', ['identifier'], unique=True)
    op.create_index('ix_requirement_analyses_status', 'requirement_analyses', ['status'])
    op.create_index('ix_requirement_analyses_owner_id', 'requirement_analyses', ['owner_id'])
    
    # 创建缺陷分析表
    op.create_table(
        'defect_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('bug_report_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('identifier', sa.String(50), nullable=False),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text, nullable=True),
        sa.Column('root_cause', sa.Text, nullable=True),
        sa.Column('impact_analysis', sa.Text, nullable=True),
        sa.Column('affected_components', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('resolution_steps', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('prevention_measures', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('similar_defects', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('severity', priority_enum, nullable=True),
        sa.Column('priority', priority_enum, nullable=True),
        sa.Column('estimated_fix_time', sa.Integer, nullable=True),
        sa.Column('actual_fix_time', sa.Integer, nullable=True),
        sa.Column('defect_category', sa.String(100), nullable=True),
        sa.Column('analysis_score', sa.Float, nullable=True),
        sa.Column('confidence_score', sa.Float, nullable=True),
        sa.Column('rag_context', postgresql.JSONB, nullable=True),
        sa.Column('used_rag', sa.Boolean, nullable=False, server_default='false'),
        sa.Column('status', defect_analysis_status, nullable=False, server_default='draft'),
        sa.Column('tags', postgresql.JSONB, nullable=True, server_default='[]'),
        sa.Column('custom_fields', postgresql.JSONB, nullable=True, server_default='{}'),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('assigned_to', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime, nullable=True),
        sa.Column('version', sa.Integer, nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['project_id'], ['test_projects.project_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['bug_report_id'], ['bug_reports.bug_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['sys_user.user_id']),
        sa.ForeignKeyConstraint(['assigned_to'], ['sys_user.user_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['resolved_by'], ['sys_user.user_id'], ondelete='SET NULL'),
        comment='缺陷分析表'
    )

    # 创建索引
    op.create_index('ix_defect_analyses_project_id', 'defect_analyses', ['project_id'])
    op.create_index('ix_defect_analyses_bug_report_id', 'defect_analyses', ['bug_report_id'])
    op.create_index('ix_defect_analyses_identifier', 'defect_analyses', ['identifier'], unique=True)
    op.create_index('ix_defect_analyses_status', 'defect_analyses', ['status'])
    op.create_index('ix_defect_analyses_assigned_to', 'defect_analyses', ['assigned_to'])


def downgrade() -> None:
    # 删除索引
    op.drop_index('ix_defect_analyses_assigned_to', table_name='defect_analyses')
    op.drop_index('ix_defect_analyses_status', table_name='defect_analyses')
    op.drop_index('ix_defect_analyses_identifier', table_name='defect_analyses')
    op.drop_index('ix_defect_analyses_bug_report_id', table_name='defect_analyses')
    op.drop_index('ix_defect_analyses_project_id', table_name='defect_analyses')

    op.drop_index('ix_requirement_analyses_owner_id', table_name='requirement_analyses')
    op.drop_index('ix_requirement_analyses_status', table_name='requirement_analyses')
    op.drop_index('ix_requirement_analyses_identifier', table_name='requirement_analyses')
    op.drop_index('ix_requirement_analyses_project_id', table_name='requirement_analyses')

    # 删除表
    op.drop_table('defect_analyses')
    op.drop_table('requirement_analyses')

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS defect_analysis_status')
    op.execute('DROP TYPE IF EXISTS requirement_analysis_status')
    op.execute('DROP TYPE IF EXISTS priority')

