"""
测试用例、缺陷报告、需求分析表结构

Revision ID: test_case_bug_requirement
Revises: 
Create Date: 2024-01-20 10:00:00
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers
revision = 'test_case_bug_requirement'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 创建测试用例表
    op.create_table(
        'test_case',
        sa.Column('case_id', sa.BigInteger(), autoincrement=True, nullable=False, comment='用例ID'),
        sa.Column('project_id', sa.BigInteger(), nullable=False, comment='项目ID'),
        sa.Column('folder_id', sa.BigInteger(), nullable=True, comment='文件夹ID'),
        sa.Column('case_identifier', sa.String(100), nullable=False, comment='用例标识符'),
        sa.Column('case_name', sa.String(200), nullable=False, comment='用例名称'),
        sa.Column('case_type', sa.String(50), nullable=True, comment='用例类型'),
        sa.Column('description', sa.Text(), nullable=True, comment='描述'),
        sa.Column('preconditions', sa.Text(), nullable=True, comment='前置条件'),
        sa.Column('test_steps', sa.Text(), nullable=True, comment='测试步骤'),
        sa.Column('expected_results', sa.Text(), nullable=True, comment='预期结果'),
        sa.Column('test_data', sa.Text(), nullable=True, comment='测试数据'),
        sa.Column('priority', sa.String(20), nullable=False, server_default='medium', comment='优先级'),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft', comment='状态'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签'),
        sa.Column('execution_status', sa.String(20), nullable=True, comment='执行状态'),
        sa.Column('execution_count', sa.Integer(), server_default='0', comment='执行次数'),
        sa.Column('pass_count', sa.Integer(), server_default='0', comment='通过次数'),
        sa.Column('fail_count', sa.Integer(), server_default='0', comment='失败次数'),
        sa.Column('create_by', sa.BigInteger(), nullable=True, comment='创建者'),
        sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('update_by', sa.BigInteger(), nullable=True, comment='更新者'),
        sa.Column('update_time', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.PrimaryKeyConstraint('case_id'),
        sa.Index('idx_project_id', 'project_id'),
        sa.Index('idx_case_identifier', 'case_identifier'),
        comment='测试用例表'
    )

    # 创建缺陷报告表
    op.create_table(
        'bug_report',
        sa.Column('bug_id', sa.BigInteger(), autoincrement=True, nullable=False, comment='缺陷ID'),
        sa.Column('project_id', sa.BigInteger(), nullable=False, comment='项目ID'),
        sa.Column('bug_identifier', sa.String(100), nullable=False, comment='缺陷标识符'),
        sa.Column('bug_title', sa.String(200), nullable=False, comment='缺陷标题'),
        sa.Column('bug_description', sa.Text(), nullable=False, comment='缺陷描述'),
        sa.Column('severity', sa.String(20), nullable=False, comment='严重程度'),
        sa.Column('priority', sa.String(20), nullable=False, comment='优先级'),
        sa.Column('bug_type', sa.String(50), nullable=False, comment='缺陷类型'),
        sa.Column('status', sa.String(20), nullable=False, server_default='open', comment='状态'),
        sa.Column('environment', sa.Text(), nullable=True, comment='环境信息'),
        sa.Column('steps_to_reproduce', sa.Text(), nullable=True, comment='复现步骤'),
        sa.Column('expected_behavior', sa.Text(), nullable=True, comment='预期行为'),
        sa.Column('actual_behavior', sa.Text(), nullable=True, comment='实际行为'),
        sa.Column('attachments', sa.Text(), nullable=True, comment='附件'),
        sa.Column('reporter', sa.BigInteger(), nullable=False, comment='报告人'),
        sa.Column('assigned_to', sa.BigInteger(), nullable=True, comment='分配给'),
        sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('resolved_time', sa.DateTime(), nullable=True, comment='解决时间'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.PrimaryKeyConstraint('bug_id'),
        sa.Index('idx_project_id', 'project_id'),
        sa.Index('idx_bug_identifier', 'bug_identifier'),
        sa.Index('idx_status', 'status'),
        comment='缺陷报告表'
    )

    # 创建需求分析表
    op.create_table(
        'requirement_analysis',
        sa.Column('requirement_id', sa.BigInteger(), autoincrement=True, nullable=False, comment='需求ID'),
        sa.Column('project_id', sa.BigInteger(), nullable=False, comment='项目ID'),
        sa.Column('requirement_identifier', sa.String(100), nullable=False, comment='需求标识符'),
        sa.Column('requirement_name', sa.String(200), nullable=False, comment='需求名称'),
        sa.Column('requirement_type', sa.String(50), nullable=False, comment='需求类型'),
        sa.Column('priority', sa.String(20), nullable=False, comment='优先级'),
        sa.Column('status', sa.String(20), nullable=False, server_default='draft', comment='状态'),
        sa.Column('module', sa.String(100), nullable=True, comment='所属模块'),
        sa.Column('description', sa.Text(), nullable=True, comment='需求描述'),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True, comment='验收标准'),
        sa.Column('functional_requirements', sa.Text(), nullable=True, comment='功能需求'),
        sa.Column('non_functional_requirements', sa.Text(), nullable=True, comment='非功能需求'),
        sa.Column('business_rules', sa.Text(), nullable=True, comment='业务规则'),
        sa.Column('dependencies', sa.Text(), nullable=True, comment='依赖关系'),
        sa.Column('stakeholders', sa.Text(), nullable=True, comment='相关干系人'),
        sa.Column('created_by', sa.BigInteger(), nullable=True, comment='创建者'),
        sa.Column('create_time', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('update_time', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.Column('remark', sa.String(500), nullable=True, comment='备注'),
        sa.PrimaryKeyConstraint('requirement_id'),
        sa.Index('idx_project_id', 'project_id'),
        sa.Index('idx_requirement_identifier', 'requirement_identifier'),
        comment='需求分析表'
    )


def downgrade() -> None:
    op.drop_table('requirement_analysis')
    op.drop_table('bug_report')
    op.drop_table('test_case')

