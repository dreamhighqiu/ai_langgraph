"""添加 BDD 和自定义字段支持

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlRScVZ3PT06M2Q2MWQ3NTI=

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库"""
    # 添加 BDD 模板类型枚举
    template_enum = postgresql.ENUM(
        'test_case', 'test_case_bdd',
        name='testcasetemplate',
        create_type=False
    )
    template_enum.create(op.get_bind(), checkfirst=True)
    
    # 添加自动化状态枚举
    automation_enum = postgresql.ENUM(
        'not_automated', 'automated', 'in_progress', 'obsolete',
        name='automationstatus',
        create_type=False
    )
    automation_enum.create(op.get_bind(), checkfirst=True)
    
    # 添加新字段到 test_cases 表
    op.add_column('test_cases', sa.Column(
        'template',
        sa.Enum('test_case', 'test_case_bdd', name='testcasetemplate'),
        nullable=False,
        server_default='test_case',
        comment='测试用例模板类型'
    ))
    
    op.add_column('test_cases', sa.Column(
        'feature',
        sa.Text(),
        nullable=True,
        comment='BDD Feature 描述'
    ))
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlRScVZ3PT06M2Q2MWQ3NTI=
    
    op.add_column('test_cases', sa.Column(
        'scenario',
        sa.Text(),
        nullable=True,
        comment='BDD Scenario 描述'
    ))
    
    op.add_column('test_cases', sa.Column(
        'background',
        sa.Text(),
        nullable=True,
        comment='BDD Background 描述'
    ))
    
    op.add_column('test_cases', sa.Column(
        'automation_status',
        sa.Enum('not_automated', 'automated', 'in_progress', 'obsolete', name='automationstatus'),
        nullable=False,
        server_default='not_automated',
        comment='自动化状态'
    ))
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlRScVZ3PT06M2Q2MWQ3NTI=
    
    op.add_column('test_cases', sa.Column(
        'custom_fields',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='自定义字段'
    ))
    
    op.add_column('test_cases', sa.Column(
        'issues',
        postgresql.JSONB(astext_type=sa.Text()),
        nullable=True,
        comment='关联的 Jira issues'
    ))
    
    # 创建索引
    op.create_index(
        'ix_test_cases_template',
        'test_cases',
        ['template']
    )
    op.create_index(
        'ix_test_cases_automation_status',
        'test_cases',
        ['automation_status']
    )


def downgrade() -> None:
    """降级数据库"""
    # 删除索引
    op.drop_index('ix_test_cases_automation_status', table_name='test_cases')
    op.drop_index('ix_test_cases_template', table_name='test_cases')
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlRScVZ3PT06M2Q2MWQ3NTI=
    
    # 删除字段
    op.drop_column('test_cases', 'issues')
    op.drop_column('test_cases', 'custom_fields')
    op.drop_column('test_cases', 'automation_status')
    op.drop_column('test_cases', 'background')
    op.drop_column('test_cases', 'scenario')
    op.drop_column('test_cases', 'feature')
    op.drop_column('test_cases', 'template')
    
    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS automationstatus')
    op.execute('DROP TYPE IF EXISTS testcasetemplate')

