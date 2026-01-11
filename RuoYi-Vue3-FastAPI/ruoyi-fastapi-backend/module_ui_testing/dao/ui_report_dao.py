"""
UI自动化测试报告DAO - 数据访问层
"""
from typing import Optional

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.project_do import TestProject
from module_ui_testing.entity.do.ui_execution_do import UITestExecution
from module_ui_testing.entity.do.ui_report_do import UITestReport
from module_ui_testing.entity.do.ui_script_do import UITestScript
from module_ui_testing.entity.vo.ui_report_vo import UIReportPageQueryModel


class UIReportDAO:
    """UI自动化测试报告数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, report_id: int) -> Optional[UITestReport]:
        """根据ID获取报告"""
        result = await db.execute(
            select(UITestReport).where(UITestReport.report_id == report_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_detail(db: AsyncSession, report_id: int) -> Optional[dict]:
        """获取报告详情(包含执行、脚本和项目信息)"""
        result = await db.execute(
            select(
                UITestReport,
                UITestExecution.execution_status,
                UITestExecution.duration,
                UITestExecution.browser,
                UITestScript.script_name,
                UITestScript.script_type,
                TestProject.project_name
            )
            .join(UITestExecution, UITestReport.execution_id == UITestExecution.execution_id)
            .join(UITestScript, UITestExecution.script_id == UITestScript.script_id)
            .join(TestProject, UITestScript.project_id == TestProject.project_id)
            .where(UITestReport.report_id == report_id)
        )
        row = result.first()
        if row:
            report, execution_status, duration, browser, script_name, script_type, project_name = row
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
                'browser': browser,
                'script_name': script_name,
                'script_type': script_type,
                'project_name': project_name,
            }
        return None
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: UIReportPageQueryModel,
        is_page: bool = True
    ) -> tuple[list[dict], int]:
        """获取报告列表"""
        # 构建查询条件
        conditions = []
        
        if query.execution_id:
            conditions.append(UITestReport.execution_id == query.execution_id)
        if query.report_name:
            conditions.append(UITestReport.report_name.like(f'%{query.report_name}%'))
        if query.report_type:
            conditions.append(UITestReport.report_type == query.report_type)
        if query.project_id:
            conditions.append(TestProject.project_id == query.project_id)
        if query.begin_time:
            conditions.append(UITestReport.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(UITestReport.create_time <= query.end_time)
        
        # 查询总数
        count_query = (
            select(func.count(UITestReport.report_id))
            .select_from(UITestReport)
            .join(UITestExecution, UITestReport.execution_id == UITestExecution.execution_id)
            .join(UITestScript, UITestExecution.script_id == UITestScript.script_id)
            .join(TestProject, UITestScript.project_id == TestProject.project_id)
        )
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = (
            select(
                UITestReport,
                UITestScript.script_name,
                TestProject.project_name
            )
            .join(UITestExecution, UITestReport.execution_id == UITestExecution.execution_id)
            .join(UITestScript, UITestExecution.script_id == UITestScript.script_id)
            .join(TestProject, UITestScript.project_id == TestProject.project_id)
        )
        
        if conditions:
            list_query = list_query.where(and_(*conditions))
        
        list_query = list_query.order_by(UITestReport.create_time.desc())
        
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
    async def get_by_execution(db: AsyncSession, execution_id: int) -> list[UITestReport]:
        """获取执行记录关联的报告"""
        result = await db.execute(
            select(UITestReport).where(
                UITestReport.execution_id == execution_id
            ).order_by(UITestReport.create_time.desc())
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, report: UITestReport) -> UITestReport:
        """创建报告"""
        db.add(report)
        await db.flush()
        await db.refresh(report)
        return report
    
    @staticmethod
    async def delete_by_id(db: AsyncSession, report_id: int) -> bool:
        """删除报告"""
        result = await db.execute(
            delete(UITestReport).where(UITestReport.report_id == report_id)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def get_by_ids(db: AsyncSession, report_ids: list[int]) -> list[dict]:
        """批量获取报告详情"""
        result = await db.execute(
            select(
                UITestReport,
                UITestExecution.execution_status,
                UITestExecution.duration,
                UITestExecution.browser,
                UITestScript.script_name,
                UITestScript.script_type,
                TestProject.project_name
            )
            .join(UITestExecution, UITestReport.execution_id == UITestExecution.execution_id)
            .join(UITestScript, UITestExecution.script_id == UITestScript.script_id)
            .join(TestProject, UITestScript.project_id == TestProject.project_id)
            .where(UITestReport.report_id.in_(report_ids))
        )
        rows = result.all()
        
        reports = []
        for report, execution_status, duration, browser, script_name, script_type, project_name in rows:
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
                'browser': browser,
                'script_name': script_name,
                'script_type': script_type,
                'project_name': project_name,
            })
        return reports
    
    @staticmethod
    async def count_by_type(db: AsyncSession) -> dict:
        """按类型统计报告数量"""
        result = await db.execute(
            select(UITestReport.report_type, func.count(UITestReport.report_id))
            .group_by(UITestReport.report_type)
        )
        rows = result.all()
        return {row[0]: row[1] for row in rows}

