"""添加报告URL字段

Revision ID: add_report_url_fields
Revises: requirement_defect_analysis
Create Date: 2026-01-09 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_report_url_fields'
down_revision = 'requirement_defect_analysis'
branch_labels = None
depends_on = None


def upgrade():
    """添加 report_url 字段到需求分析和缺陷分析表"""
    # 添加需求分析表的 report_url 字段
    op.add_column(
        'test_requirement_analysis',
        sa.Column('report_url', sa.String(500), nullable=True, comment='分析报告URL')
    )
    
    # 添加缺陷分析表的 report_url 字段
    op.add_column(
        'test_defect_analysis',
        sa.Column('report_url', sa.String(500), nullable=True, comment='分析报告URL')
    )


def downgrade():
    """回滚：删除 report_url 字段"""
    # 删除需求分析表的 report_url 字段
    op.drop_column('test_requirement_analysis', 'report_url')
    
    # 删除缺陷分析表的 report_url 字段
    op.drop_column('test_defect_analysis', 'report_url')

