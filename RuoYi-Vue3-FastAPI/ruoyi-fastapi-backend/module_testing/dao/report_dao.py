"""
测试报告DAO - 数据访问层
"""
from typing import Optional

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.project_do import TestProject
from module_testing.entity.do.report_do import TestReport
from module_testing.entity.do.script_do import TestScript
from module_testing.entity.vo.report_vo import ReportPageQueryModel


class ReportDAO:
    """测试报告数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, report_id: int) -> Optional[TestReport]:
        """根据ID获取报告"""
        result = await db.execute(
            select(TestReport).where(TestReport.report_id == report_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_detail(db: AsyncSession, report_id: int) -> Optional[dict]:
        """获取报告详情(包含执行、脚本和项目信息)"""
        result = await db.execute(
            select(
                TestReport,
                TestExecution.execution_status,
                TestExecution.duration,
                TestScript.script_name,
                TestScript.script_type,
                TestProject.project_name
            )
            .join(TestExecution, TestReport.execution_id == TestExecution.execution_id)
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
            .where(TestReport.report_id == report_id)
        )
        row = result.first()
        if row:
            report, execution_status, duration, script_name, script_type, project_name = row
            return {
                'report_id': report.report_id,
                'execution_id': report.execution_id,
                'report_name': report.report_name,
                'report_type': report.report_type,
                'report_path': report.report_path,
                'report_size': report.report_size,
                'summary': report.summary,
                'metrics': report.metrics,
                'create_time': report.create_time,
                'execution_status': execution_status,
                'duration': duration,
                'script_name': script_name,
                'script_type': script_type,
                'project_name': project_name,
            }
        return None
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: ReportPageQueryModel,
        is_page: bool = True
    ) -> tuple[list[dict], int]:
        """获取报告列表"""
        # 构建查询条件
        conditions = []
        
        if query.execution_id:
            conditions.append(TestReport.execution_id == query.execution_id)
        if query.report_name:
            conditions.append(TestReport.report_name.like(f'%{query.report_name}%'))
        if query.report_type:
            conditions.append(TestReport.report_type == query.report_type)
        if query.script_type:
            conditions.append(TestScript.script_type == query.script_type)
        if query.project_id:
            conditions.append(TestProject.project_id == query.project_id)
        if query.begin_time:
            conditions.append(TestReport.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(TestReport.create_time <= query.end_time)
        
        # 查询总数
        count_query = (
            select(func.count(TestReport.report_id))
            .select_from(TestReport)
            .join(TestExecution, TestReport.execution_id == TestExecution.execution_id)
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = (
            select(
                TestReport,
                TestScript.script_name,
                TestProject.project_name
            )
            .join(TestExecution, TestReport.execution_id == TestExecution.execution_id)
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
        )
        
        if conditions:
            list_query = list_query.where(and_(*conditions))
        
        list_query = list_query.order_by(TestReport.create_time.desc())
        
        if is_page:
            offset = (query.page_num - 1) * query.page_size
            list_query = list_query.offset(offset).limit(query.page_size)
        
        result = await db.execute(list_query)
        rows = result.all()
        
        reports = []
        for report, script_name, project_name in rows:
            report_dict = {
                'report_id': report.report_id,
                'execution_id': report.execution_id,
                'script_name': script_name,
                'project_name': project_name,
                'report_name': report.report_name,
                'report_type': report.report_type,
                'report_path': report.report_path,
                'report_size': report.report_size,
                'summary': report.summary,
                'metrics': report.metrics,
                'create_time': report.create_time,
            }
            reports.append(report_dict)
        
        return reports, total
    
    @staticmethod
    async def get_by_execution(db: AsyncSession, execution_id: int) -> list[TestReport]:
        """获取执行记录关联的报告"""
        result = await db.execute(
            select(TestReport).where(
                TestReport.execution_id == execution_id
            ).order_by(TestReport.create_time.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, report: TestReport) -> TestReport:
        """创建报告"""
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report
    
    @staticmethod
    async def delete_by_id(db: AsyncSession, report_id: int) -> bool:
        """删除报告"""
        from sqlalchemy import delete
        result = await db.execute(
            delete(TestReport).where(TestReport.report_id == report_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def get_by_ids(db: AsyncSession, report_ids: list[int]) -> list[dict]:
        """批量获取报告详情"""
        result = await db.execute(
            select(
                TestReport,
                TestExecution.execution_status,
                TestExecution.duration,
                TestScript.script_name,
                TestScript.script_type,
                TestProject.project_name
            )
            .join(TestExecution, TestReport.execution_id == TestExecution.execution_id)
            .join(TestScript, TestExecution.script_id == TestScript.script_id)
            .join(TestProject, TestScript.project_id == TestProject.project_id)
            .where(TestReport.report_id.in_(report_ids))
        )
        rows = result.all()
        
        reports = []
        for report, execution_status, duration, script_name, script_type, project_name in rows:
            reports.append({
                'report_id': report.report_id,
                'execution_id': report.execution_id,
                'report_name': report.report_name,
                'report_type': report.report_type,
                'report_path': report.report_path,
                'report_size': report.report_size,
                'summary': report.summary,
                'metrics': report.metrics,
                'create_time': report.create_time,
                'execution_status': execution_status,
                'duration': duration,
                'script_name': script_name,
                'script_type': script_type,
                'project_name': project_name,
            })
        return reports
    
    @staticmethod
    async def count_by_type(db: AsyncSession) -> dict:
        """按类型统计报告数量"""
        result = await db.execute(
            select(TestReport.report_type, func.count(TestReport.report_id))
            .group_by(TestReport.report_type)
        )
        rows = result.all()
        return {row[0]: row[1] for row in rows}

