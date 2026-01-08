"""添加附件表

Revision ID: 003
Revises: 002
Create Date: 2024-01-20 00:00:00.000000

"""


from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# pragma: no cover  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2psMU9RPT06MGQ3MGYzYmY=

# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2psMU9RPT06MGQ3MGYzYmY=

def upgrade() -> None:
    """升级数据库 - 创建附件表"""

    # 创建附件实体类型枚举
    attachment_entity_type_enum = postgresql.ENUM(
        'test_case', 'test_case_step', 'test_result', 'test_step_result',
        name='attachmententitytype',
        create_type=False
    )
    attachment_entity_type_enum.create(op.get_bind(), checkfirst=True)

    # 创建 attachments 表
    op.create_table(
        'attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('entity_type', sa.Enum(
            'test_case', 'test_case_step', 'test_result', 'test_step_result',
            name='attachmententitytype'
        ), nullable=False, index=True, comment='关联实体类型'),
        sa.Column('entity_id', postgresql.UUID(as_uuid=True), nullable=False, index=True, comment='关联实体 ID'),
        sa.Column('project_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False, index=True, comment='项目 ID'),
        sa.Column('file_name', sa.String(500), nullable=False, comment='原始文件名'),
        sa.Column('file_size', sa.Integer(), nullable=False, comment='文件大小（字节）'),
        sa.Column('content_type', sa.String(255), nullable=False, comment='MIME 类型'),
        sa.Column('object_name', sa.String(1000), nullable=False, unique=True, comment='MinIO 对象名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='附件描述'),
        sa.Column('created_by', sa.String(255), nullable=True, comment='上传人邮箱'),
        sa.Column('step_index', sa.Integer(), nullable=True, comment='步骤索引（从 1 开始）'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True, onupdate=sa.text('CURRENT_TIMESTAMP')),
        comment='附件表'
    )

    # 创建复合索引，用于快速查询实体的附件
    op.create_index(
        'ix_attachments_entity',
        'attachments',
        ['entity_type', 'entity_id'],
    )

# pylint: disable  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2psMU9RPT06MGQ3MGYzYmY=

def downgrade() -> None:
    """降级数据库 - 删除附件表"""

    # 删除索引
    op.drop_index('ix_attachments_entity', 'attachments')

    # 删除表
    op.drop_table('attachments')
# fmt: off  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y2psMU9RPT06MGQ3MGYzYmY=

    # 删除枚举类型
    op.execute('DROP TYPE IF EXISTS attachmententitytype')

