"""Add testing module tables for MySQL

Revision ID: add_testing_mysql_001
Revises: requirement_defect_001
Create Date: 2025-01-09

说明: 创建测试模块相关表（适配MySQL）
- 文件夹表 (test_folder)
- 测试用例表 (test_case)
- 需求分析表 (test_requirement_analysis)
- 缺陷分析表 (test_defect_analysis)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'add_testing_mysql_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 创建项目表
    op.create_table(
        'test_project',
        sa.Column('project_id', sa.Integer(), autoincrement=True, nullable=False, comment='项目ID'),
        sa.Column('project_name', sa.String(200), nullable=False, comment='项目名称'),
        sa.Column('project_key', sa.String(50), nullable=True, comment='项目标识'),
        sa.Column('description', sa.Text(), nullable=True, comment='项目描述'),
        sa.Column('status', sa.String(20), server_default='0', comment='状态(0正常 1停用)'),
        sa.Column('create_by', sa.String(64), server_default='', comment='创建者'),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('update_by', sa.String(64), server_default='', comment='更新者'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('remark', sa.String(500), server_default='', comment='备注'),
        sa.PrimaryKeyConstraint('project_id'),
        comment='测试项目表'
    )
    op.create_index('idx_project_name', 'test_project', ['project_name'])
    op.create_index('idx_project_status', 'test_project', ['status'])

    # 创建文件夹表
    op.create_table(
        'test_folder',
        sa.Column('folder_id', sa.Integer(), autoincrement=True, nullable=False, comment='文件夹ID'),
        sa.Column('project_id', sa.Integer(), nullable=False, comment='所属项目ID'),
        sa.Column('parent_id', sa.Integer(), nullable=True, comment='父文件夹ID'),
        sa.Column('folder_name', sa.String(255), nullable=False, comment='文件夹名称'),
        sa.Column('description', sa.Text(), nullable=True, comment='文件夹描述'),
        sa.Column('order_num', sa.Integer(), server_default='0', comment='显示顺序'),
        sa.Column('status', sa.String(20), server_default='0', comment='状态(0正常 1停用)'),
        sa.Column('create_by', sa.String(64), server_default='', comment='创建者'),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('update_by', sa.String(64), server_default='', comment='更新者'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('remark', sa.String(500), server_default='', comment='备注'),
        sa.PrimaryKeyConstraint('folder_id'),
        comment='测试用例文件夹表'
    )
    op.create_index('idx_folder_project_id', 'test_folder', ['project_id'])
    op.create_index('idx_folder_parent_id', 'test_folder', ['parent_id'])
    op.create_index('idx_folder_create_time', 'test_folder', ['create_time'])

    # 创建测试用例表
    op.create_table(
        'test_case',
        sa.Column('case_id', sa.Integer(), autoincrement=True, nullable=False, comment='用例ID'),
        sa.Column('project_id', sa.Integer(), nullable=False, comment='项目ID'),
        sa.Column('folder_id', sa.Integer(), nullable=True, comment='文件夹ID'),
        sa.Column('case_name', sa.String(500), nullable=False, comment='用例名称'),
        sa.Column('case_type', sa.String(50), server_default='functional', comment='用例类型'),
        sa.Column('priority', sa.String(20), server_default='medium', comment='优先级(high/medium/low)'),
        sa.Column('status', sa.String(20), server_default='draft', comment='状态(draft/pending/approved/deprecated)'),
        sa.Column('preconditions', sa.Text(), nullable=True, comment='前置条件'),
        sa.Column('test_case_steps', sa.Text(), nullable=True, comment='测试步骤(JSON)'),
        sa.Column('expected_result', sa.Text(), nullable=True, comment='预期结果'),
        sa.Column('actual_result', sa.Text(), nullable=True, comment='实际结果'),
        sa.Column('test_data', sa.Text(), nullable=True, comment='测试数据(JSON)'),
        sa.Column('bdd_feature', sa.Text(), nullable=True, comment='BDD Feature'),
        sa.Column('bdd_scenario', sa.Text(), nullable=True, comment='BDD Scenario'),
        sa.Column('bdd_given', sa.Text(), nullable=True, comment='BDD Given'),
        sa.Column('bdd_when', sa.Text(), nullable=True, comment='BDD When'),
        sa.Column('bdd_then', sa.Text(), nullable=True, comment='BDD Then'),
        sa.Column('is_automated', sa.Integer(), server_default='0', comment='是否已自动化(0否 1是)'),
        sa.Column('automation_script_id', sa.Integer(), nullable=True, comment='自动化脚本ID'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签(逗号分隔)'),
        sa.Column('create_by', sa.String(64), server_default='', comment='创建者'),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('update_by', sa.String(64), server_default='', comment='更新者'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('remark', sa.String(500), server_default='', comment='备注'),
        sa.PrimaryKeyConstraint('case_id'),
        comment='测试用例表'
    )
    op.create_index('idx_case_project_id', 'test_case', ['project_id'])
    op.create_index('idx_case_folder_id', 'test_case', ['folder_id'])
    op.create_index('idx_case_status', 'test_case', ['status'])
    op.create_index('idx_case_priority', 'test_case', ['priority'])
    op.create_index('idx_case_create_time', 'test_case', ['create_time'])

    # 创建需求分析表
    op.create_table(
        'test_requirement_analysis',
        sa.Column('requirement_id', sa.Integer(), autoincrement=True, nullable=False, comment='需求ID'),
        sa.Column('project_id', sa.Integer(), nullable=False, comment='项目ID'),
        sa.Column('knowledge_id', sa.Integer(), nullable=True, comment='关联知识库ID'),
        sa.Column('requirement_identifier', sa.String(50), nullable=True, comment='需求标识'),
        sa.Column('requirement_name', sa.String(200), nullable=False, comment='需求名称'),
        sa.Column('requirement_type', sa.String(50), server_default='functional', comment='需求类型'),
        sa.Column('priority', sa.String(20), server_default='medium', comment='优先级'),
        sa.Column('module', sa.String(200), nullable=True, comment='所属模块'),
        sa.Column('description', sa.Text(), nullable=True, comment='需求描述'),
        sa.Column('acceptance_criteria', sa.Text(), nullable=True, comment='验收标准'),
        sa.Column('functional_requirements', sa.Text(), nullable=True, comment='功能需求'),
        sa.Column('non_functional_requirements', sa.Text(), nullable=True, comment='非功能需求'),
        sa.Column('business_rules', sa.Text(), nullable=True, comment='业务规则'),
        sa.Column('dependencies', sa.Text(), nullable=True, comment='依赖关系(JSON)'),
        sa.Column('stakeholders', sa.Text(), nullable=True, comment='干系人(JSON)'),
        sa.Column('use_rag', sa.Integer(), server_default='0', comment='是否使用RAG(0否1是)'),
        sa.Column('rag_context', sa.Text(), nullable=True, comment='RAG检索上下文'),
        sa.Column('status', sa.String(20), server_default='draft', comment='状态(draft/pending/approved/rejected)'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签(逗号分隔)'),
        sa.Column('create_by', sa.String(64), server_default='', comment='创建者'),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('update_by', sa.String(64), server_default='', comment='更新者'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('remark', sa.String(500), server_default='', comment='备注'),
        sa.PrimaryKeyConstraint('requirement_id'),
        comment='需求分析表'
    )
    op.create_index('idx_req_project_id', 'test_requirement_analysis', ['project_id'])
    op.create_index('idx_req_status', 'test_requirement_analysis', ['status'])
    op.create_index('idx_req_priority', 'test_requirement_analysis', ['priority'])
    op.create_index('idx_req_create_time', 'test_requirement_analysis', ['create_time'])

    # 创建缺陷分析表
    op.create_table(
        'test_defect_analysis',
        sa.Column('analysis_id', sa.Integer(), autoincrement=True, nullable=False, comment='分析ID'),
        sa.Column('project_id', sa.Integer(), nullable=False, comment='项目ID'),
        sa.Column('knowledge_id', sa.Integer(), nullable=True, comment='关联知识库ID'),
        sa.Column('defect_id', sa.String(100), nullable=True, comment='关联缺陷ID'),
        sa.Column('analysis_name', sa.String(200), nullable=False, comment='分析名称'),
        sa.Column('defect_title', sa.String(200), nullable=True, comment='缺陷标题'),
        sa.Column('defect_description', sa.Text(), nullable=True, comment='缺陷描述'),
        sa.Column('severity', sa.String(20), server_default='medium', comment='严重程度(critical/high/medium/low)'),
        sa.Column('priority', sa.String(20), server_default='medium', comment='优先级(urgent/high/medium/low)'),
        sa.Column('defect_type', sa.String(50), nullable=True, comment='缺陷类型'),
        sa.Column('category', sa.String(100), nullable=True, comment='详细分类'),
        sa.Column('affected_phase', sa.String(50), nullable=True, comment='影响阶段'),
        sa.Column('detection_phase', sa.String(50), nullable=True, comment='发现阶段'),
        sa.Column('executive_summary', sa.Text(), nullable=True, comment='缺陷概述'),
        sa.Column('root_cause_analysis', sa.Text(), nullable=True, comment='根本原因分析(JSON)'),
        sa.Column('impact_analysis', sa.Text(), nullable=True, comment='影响分析(JSON)'),
        sa.Column('reproduction_steps', sa.Text(), nullable=True, comment='复现步骤(JSON)'),
        sa.Column('affected_modules', sa.Text(), nullable=True, comment='受影响模块(JSON)'),
        sa.Column('fix_suggestions', sa.Text(), nullable=True, comment='修复建议(JSON)'),
        sa.Column('test_suggestions', sa.Text(), nullable=True, comment='测试建议(JSON)'),
        sa.Column('prevention_measures', sa.Text(), nullable=True, comment='预防措施(JSON)'),
        sa.Column('similar_defects', sa.Text(), nullable=True, comment='相似缺陷(JSON)'),
        sa.Column('use_rag', sa.Integer(), server_default='0', comment='是否使用RAG(0否1是)'),
        sa.Column('rag_context', sa.Text(), nullable=True, comment='RAG检索上下文'),
        sa.Column('mindmap_data', sa.Text(), nullable=True, comment='思维导图数据(JSON)'),
        sa.Column('mindmap_url', sa.String(500), nullable=True, comment='思维导图图片URL'),
        sa.Column('status', sa.String(20), server_default='draft', comment='状态(draft/analyzing/completed/failed)'),
        sa.Column('process_status', sa.String(20), nullable=True, comment='处理状态'),
        sa.Column('error_message', sa.Text(), nullable=True, comment='错误信息'),
        sa.Column('fix_status', sa.String(20), nullable=True, comment='修复状态'),
        sa.Column('fix_time_estimate', sa.String(50), nullable=True, comment='预计修复时间'),
        sa.Column('actual_fix_time', sa.DateTime(), nullable=True, comment='实际修复时间'),
        sa.Column('tags', sa.String(500), nullable=True, comment='标签(逗号分隔)'),
        sa.Column('create_by', sa.String(64), server_default='', comment='创建者'),
        sa.Column('create_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), comment='创建时间'),
        sa.Column('update_by', sa.String(64), server_default='', comment='更新者'),
        sa.Column('update_time', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), comment='更新时间'),
        sa.Column('remark', sa.String(500), server_default='', comment='备注'),
        sa.PrimaryKeyConstraint('analysis_id'),
        comment='缺陷分析表'
    )
    op.create_index('idx_defect_project_id', 'test_defect_analysis', ['project_id'])
    op.create_index('idx_defect_severity', 'test_defect_analysis', ['severity'])
    op.create_index('idx_defect_priority', 'test_defect_analysis', ['priority'])
    op.create_index('idx_defect_status', 'test_defect_analysis', ['status'])
    op.create_index('idx_defect_create_time', 'test_defect_analysis', ['create_time'])


def downgrade() -> None:
    # 删除表
    op.drop_table('test_defect_analysis')
    op.drop_table('test_requirement_analysis')
    op.drop_table('test_case')
    op.drop_table('test_folder')
    op.drop_table('test_project')

