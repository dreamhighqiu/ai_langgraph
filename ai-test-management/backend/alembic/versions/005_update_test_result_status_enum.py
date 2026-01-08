"""更新测试结果状态枚举值以符合 BrowserStack API 规范

Revision ID: 005
Revises: 004
Create Date: 2024-12-08 00:00:00.000000

变更说明:
- 将 TestResultStatus 枚举值从 (untested, passed, failed, skipped, blocked, retest) 
  更新为 (passed, failed, skipped, blocked, not_executed)
- 将 test_runs 表的 retest_count 和 untested_count 列合并为 not_executed_count
- 将 test_run_test_cases 表的 latest_status 默认值从 'untested' 更新为 'not_executed'
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
# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjBkR1VRPT06YjA4Zjc3ZTU=

# revision identifiers, used by Alembic.
revision: str = '005'
down_revision: Union[str, None] = '004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjBkR1VRPT06YjA4Zjc3ZTU=

def upgrade() -> None:
    """升级数据库 - 更新测试结果状态枚举"""
    
    # 1. 添加新的枚举值 'not_executed'
    op.execute("ALTER TYPE testresultstatus ADD VALUE IF NOT EXISTS 'not_executed'")
    
    # 2. 更新 test_run_test_cases 表中的 latest_status 列
    # 将 'untested' 和 'retest' 值更新为 'not_executed'
    op.execute("""
        UPDATE test_run_test_cases 
        SET latest_status = 'not_executed' 
        WHERE latest_status IN ('untested', 'retest')
    """)
    
    # 3. 更新 test_results 表中的 status 列
    op.execute("""
        UPDATE test_results 
        SET status = 'not_executed' 
        WHERE status IN ('untested', 'retest')
    """)
    
    # 4. 更新 test_step_results 表中的 status 列
    op.execute("""
        UPDATE test_step_results 
        SET status = 'not_executed' 
        WHERE status IN ('untested', 'retest')
    """)
    
    # 5. 在 test_runs 表中添加 not_executed_count 列
    op.add_column(
        'test_runs',
        sa.Column('not_executed_count', sa.Integer(), nullable=False, server_default='0', comment='未执行数量')
    )
    
    # 6. 将 untested_count 和 retest_count 的值合并到 not_executed_count
    op.execute("""
        UPDATE test_runs 
        SET not_executed_count = COALESCE(untested_count, 0) + COALESCE(retest_count, 0)
    """)
    
    # 7. 删除旧的 retest_count 和 untested_count 列
    op.drop_column('test_runs', 'retest_count')
    op.drop_column('test_runs', 'untested_count')
    
    # 注意: PostgreSQL 不支持直接删除枚举值，但我们可以保留旧值
    # 在应用层面，我们只使用新的枚举值

# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjBkR1VRPT06YjA4Zjc3ZTU=

def downgrade() -> None:
    """降级数据库 - 恢复旧的测试结果状态枚举"""
    
    # 1. 添加回 retest_count 和 untested_count 列
    op.add_column(
        'test_runs',
        sa.Column('retest_count', sa.Integer(), nullable=False, server_default='0', comment='重测数量')
    )
    op.add_column(
        'test_runs',
        sa.Column('untested_count', sa.Integer(), nullable=False, server_default='0', comment='未测试数量')
    )
    
    # 2. 将 not_executed_count 的值复制到 untested_count
    op.execute("""
        UPDATE test_runs 
        SET untested_count = not_executed_count
    """)
    
    # 3. 删除 not_executed_count 列
    op.drop_column('test_runs', 'not_executed_count')
    
    # 4. 将 'not_executed' 值更新回 'untested'
    op.execute("""
        UPDATE test_run_test_cases 
        SET latest_status = 'untested' 
        WHERE latest_status = 'not_executed'
    """)
    
    op.execute("""
        UPDATE test_results 
        SET status = 'untested' 
        WHERE status = 'not_executed'
    """)
    
    op.execute("""
        UPDATE test_step_results 
        SET status = 'untested' 
        WHERE status = 'not_executed'
    """)

# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2VjBkR1VRPT06YjA4Zjc3ZTU=
