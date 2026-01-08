"""添加配置表

Revision ID: 004
Revises: 003
Create Date: 2024-01-20 00:00:00.000000

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

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# pylint: disable  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkhaWE13PT06ODNlMjZjOWI=

def upgrade() -> None:
    """升级数据库 - 创建配置表"""

    # 创建 configurations 表
    op.create_table(
        'configurations',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, comment='配置 ID'),
        sa.Column('name', sa.String(500), nullable=False, comment='配置名称'),
        sa.Column('os', sa.String(100), nullable=True, comment='操作系统'),
        sa.Column('os_version', sa.String(100), nullable=True, comment='操作系统版本'),
        sa.Column('device', sa.String(200), nullable=True, comment='设备'),
        sa.Column('browser', sa.String(100), nullable=True, comment='浏览器'),
        sa.Column('browser_version', sa.String(100), nullable=True, comment='浏览器版本'),
        sa.Column('is_system', sa.Boolean(), nullable=False, default=False, comment='是否为系统定义配置'),
        sa.Column('description', sa.Text(), nullable=True, comment='配置描述'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='测试配置表'
    )
# pragma: no cover  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkhaWE13PT06ODNlMjZjOWI=

    # 创建索引
    op.create_index('ix_configurations_name', 'configurations', ['name'])
    op.create_index('ix_configurations_is_system', 'configurations', ['is_system'])

    # 插入默认系统配置
    op.execute("""
        INSERT INTO configurations (name, os, os_version, device, browser, browser_version, is_system, created_at) VALUES
        ('Windows - Chrome latest', 'Windows', '11', NULL, 'Chrome', 'latest', true, CURRENT_TIMESTAMP),
        ('Windows - Firefox latest', 'Windows', '11', NULL, 'Firefox', 'latest', true, CURRENT_TIMESTAMP),
        ('Windows - Edge latest', 'Windows', '11', NULL, 'Edge', 'latest', true, CURRENT_TIMESTAMP),
        ('macOS - Safari latest', 'macOS', 'Sonoma', NULL, 'Safari', 'latest', true, CURRENT_TIMESTAMP),
        ('macOS - Chrome latest', 'macOS', 'Sonoma', NULL, 'Chrome', 'latest', true, CURRENT_TIMESTAMP),
        ('iOS - iPhone 15', 'iOS', '17', 'iPhone 15', NULL, NULL, true, CURRENT_TIMESTAMP),
        ('iOS - iPhone 14', 'iOS', '16', 'iPhone 14', NULL, NULL, true, CURRENT_TIMESTAMP),
        ('iOS - iPad Pro', 'iOS', '17', 'iPad Pro', NULL, NULL, true, CURRENT_TIMESTAMP),
        ('Android - Pixel 8', 'Android', '14', 'Pixel 8', NULL, NULL, true, CURRENT_TIMESTAMP),
        ('Android - Samsung Galaxy S24', 'Android', '14', 'Samsung Galaxy S24', NULL, NULL, true, CURRENT_TIMESTAMP)
    """)


def downgrade() -> None:
    """降级数据库 - 删除配置表"""

    # 删除索引
    op.drop_index('ix_configurations_is_system', 'configurations')
    op.drop_index('ix_configurations_name', 'configurations')
# pylint: disable  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TkhaWE13PT06ODNlMjZjOWI=

    # 删除表
    op.drop_table('configurations')

