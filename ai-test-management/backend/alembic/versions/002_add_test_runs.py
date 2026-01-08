"""添加测试运行和测试结果相关表

Revision ID: 002
Revises: 001
Create Date: 2024-01-15 00:00:00.000000

"""


from typing import Sequence, Union
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVscFZRPT06Y2Y0MjVjZTQ=

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库 - 创建测试运行和测试结果相关表"""

    # 创建测试运行状态枚举
    test_run_state_enum = postgresql.ENUM(
        'new_run', 'in_progress', 'under_review', 'rejected', 'done', 'closed',
        name='testrunstate',
        create_type=False
    )
    test_run_state_enum.create(op.get_bind(), checkfirst=True)
# pragma: no cover  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVscFZRPT06Y2Y0MjVjZTQ=

    # 创建测试运行活跃状态枚举
    active_state_enum = postgresql.ENUM(
        'active', 'closed',
        name='testrunactivestate',
        create_type=False
    )
    active_state_enum.create(op.get_bind(), checkfirst=True)

    # 创建测试结果状态枚举
    test_result_status_enum = postgresql.ENUM(
        'untested', 'passed', 'failed', 'skipped', 'blocked', 'retest',
        name='testresultstatus',
        create_type=False
    )
    test_result_status_enum.create(op.get_bind(), checkfirst=True)
    
    # 创建 test_runs 表
    op.create_table(
        'test_runs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('identifier', sa.String(50), nullable=False, unique=True, index=True, comment='测试运行标识符'),
        sa.Column('name', sa.String(500), nullable=False, comment='测试运行名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='测试运行描述'),
        sa.Column('run_state', sa.Enum('new_run', 'in_progress', 'under_review', 'rejected', 'done', 'closed', name='testrunstate'), nullable=False, server_default='new_run', comment='运行状态'),
        sa.Column('active_state', sa.Enum('active', 'closed', name='testrunactivestate'), nullable=False, server_default='active', comment='活跃状态'),
        sa.Column('assignee', sa.String(255), nullable=True, comment='负责人邮箱'),
        sa.Column('test_plan_id', postgresql.UUID(as_uuid=True), nullable=True, index=True, comment='关联的测试计划 ID'),
        sa.Column('tags', postgresql.JSONB(), nullable=True, server_default='[]', comment='标签列表'),
        sa.Column('issues', postgresql.JSONB(), nullable=True, server_default='[]', comment='关联的问题列表'),
        sa.Column('configurations', postgresql.JSONB(), nullable=True, server_default='[]', comment='配置 ID 列表'),
        sa.Column('test_cases_count', sa.Integer(), nullable=False, server_default='0', comment='测试用例总数'),
        sa.Column('passed_count', sa.Integer(), nullable=False, server_default='0', comment='通过数量'),
        sa.Column('failed_count', sa.Integer(), nullable=False, server_default='0', comment='失败数量'),
        sa.Column('skipped_count', sa.Integer(), nullable=False, server_default='0', comment='跳过数量'),
        sa.Column('blocked_count', sa.Integer(), nullable=False, server_default='0', comment='阻塞数量'),
        sa.Column('retest_count', sa.Integer(), nullable=False, server_default='0', comment='重测数量'),
        sa.Column('untested_count', sa.Integer(), nullable=False, server_default='0', comment='未测试数量'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='测试运行表'
    )
    
    # 创建 test_run_test_cases 表
    op.create_table(
        'test_run_test_cases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('test_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_runs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('configuration_id', sa.Integer(), nullable=True, comment='配置 ID'),
        sa.Column('assignee', sa.String(255), nullable=True, comment='负责人邮箱'),
        sa.Column('latest_status', sa.Enum('untested', 'passed', 'failed', 'skipped', 'blocked', 'retest', name='testresultstatus'), nullable=False, server_default='untested', comment='最新测试结果状态'),
        sa.Column('latest_result_id', postgresql.UUID(as_uuid=True), nullable=True, comment='最新测试结果 ID'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='测试运行测试用例关联表'
    )
    
    # 创建联合唯一索引
    op.create_index(
        'ix_test_run_test_cases_unique',
        'test_run_test_cases',
        ['test_run_id', 'test_case_id', 'configuration_id'],
        unique=True
    )

    # 创建 test_results 表
    op.create_table(
        'test_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('test_run_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_runs.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_cases.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('test_run_test_case_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_run_test_cases.id', ondelete='SET NULL'), nullable=True, index=True),
        sa.Column('configuration_id', sa.Integer(), nullable=True, comment='配置 ID'),
        sa.Column('status', sa.Enum('untested', 'passed', 'failed', 'skipped', 'blocked', 'retest', name='testresultstatus'), nullable=False, comment='测试结果状态'),
        sa.Column('description', sa.Text(), nullable=True, comment='测试结果描述/备注'),
        sa.Column('created_by', sa.String(255), nullable=True, comment='创建人邮箱'),
        sa.Column('assignee', sa.String(255), nullable=True, comment='执行人邮箱'),
        sa.Column('issues', postgresql.JSONB(), nullable=True, server_default='[]', comment='关联的问题列表'),
        sa.Column('issue_tracker', postgresql.JSONB(), nullable=True, comment='问题跟踪器配置'),
        sa.Column('custom_fields', postgresql.JSONB(), nullable=True, comment='自定义字段'),
        sa.Column('duration_ms', sa.Integer(), nullable=True, comment='执行时长(毫秒)'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='测试结果表'
    )

    # 创建 test_step_results 表
    op.create_table(
        'test_step_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('test_result_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('test_results.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('step_id', sa.Integer(), nullable=True, comment='步骤 ID (永久标识符)'),
        sa.Column('step_index', sa.Integer(), nullable=False, comment='步骤索引 (从 1 开始)'),
        sa.Column('status', sa.Enum('untested', 'passed', 'failed', 'skipped', 'blocked', 'retest', name='testresultstatus'), nullable=False, comment='步骤执行状态'),
        sa.Column('description', sa.Text(), nullable=True, comment='步骤结果描述/备注'),
        sa.Column('issues', postgresql.JSONB(), nullable=True, server_default='[]', comment='关联的问题列表'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='测试步骤结果表'
    )
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVscFZRPT06Y2Y0MjVjZTQ=


def downgrade() -> None:
    """降级数据库 - 删除测试运行和测试结果相关表"""

    # 删除表 (注意顺序，先删除依赖表)
    op.drop_table('test_step_results')
    op.drop_table('test_results')
    op.drop_index('ix_test_run_test_cases_unique', 'test_run_test_cases')
    op.drop_table('test_run_test_cases')
    op.drop_table('test_runs')

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS testresultstatus')
    op.execute('DROP TYPE IF EXISTS testrunactivestate')
    op.execute('DROP TYPE IF EXISTS testrunstate')

# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZVVscFZRPT06Y2Y0MjVjZTQ=
