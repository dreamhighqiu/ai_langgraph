"""
质量看板服务
"""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.entity.do.bug_report_do import BugReportDO
from module_testing.entity.do.execution_do import TestExecution
from module_testing.entity.do.project_do import TestProject
from module_testing.entity.do.requirement_do import TestRequirement
from module_testing.entity.do.script_do import TestScript
from module_testing.entity.do.test_case_do import TestCaseDO
from module_testing.entity.vo.execution_vo import ExecutionPageQueryModel


class DashboardService:
    @staticmethod
    async def get_summary(db: AsyncSession, days: int = 7) -> dict:
        """
        获取质量看板汇总数据

        days: 统计区间（近N天）
        """
        days = max(1, min(int(days or 7), 90))
        start_date = datetime.now() - timedelta(days=days - 1)

        # KPI
        project_total = await db.scalar(
            select(func.count(TestProject.project_id)).where(TestProject.del_flag == "0")
        )
        script_total = await db.scalar(
            select(func.count(TestScript.script_id)).where(TestScript.del_flag == "0")
        )
        case_total = await db.scalar(select(func.count()).select_from(TestCaseDO))
        requirement_total = await db.scalar(
            select(func.count(TestRequirement.requirement_id)).where(
                TestRequirement.del_flag == "0"
            )
        )
        bug_open = await db.scalar(
            select(func.count()).select_from(BugReportDO).where(BugReportDO.status == "open")
        )

        exec_stats = await ExecutionDAO.get_statistics(db, days=days)

        # 近N天执行趋势（补齐日期）
        date_col = func.date(TestExecution.create_time).label("d")
        total_col = func.count(TestExecution.execution_id).label("total")
        success_col = func.sum(
            case((TestExecution.execution_status == "success", 1), else_=0)
        ).label("success")
        failed_col = func.sum(
            case((TestExecution.execution_status == "failed", 1), else_=0)
        ).label("failed")

        trend_rows = await db.execute(
            select(date_col, total_col, success_col, failed_col)
            .where(TestExecution.create_time >= start_date)
            .group_by(date_col)
            .order_by(date_col)
        )
        trend_map: dict[str, dict] = {}
        for d, total, success, failed in trend_rows.all():
            key = d.strftime("%Y-%m-%d") if hasattr(d, "strftime") else str(d)
            trend_map[key] = {
                "date": key,
                "total": int(total or 0),
                "success": int(success or 0),
                "failed": int(failed or 0),
            }

        trend: list[dict] = []
        for i in range(days):
            day = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
            trend.append(
                trend_map.get(day, {"date": day, "total": 0, "success": 0, "failed": 0})
            )

        # 缺陷状态分布
        bug_status_rows = await db.execute(
            select(BugReportDO.status, func.count().label("count"))
            .select_from(BugReportDO)
            .group_by(BugReportDO.status)
        )
        bug_status = {status: int(count or 0) for status, count in bug_status_rows.all()}

        # 最近执行
        executions, _ = await ExecutionDAO.get_list(
            db, ExecutionPageQueryModel(page_num=1, page_size=8), is_page=True
        )
        recent_executions = [
            {
                "execution_id": e.get("execution_id"),
                "project_name": e.get("project_name"),
                "script_name": e.get("script_name"),
                "script_type": e.get("script_type"),
                "execution_type": e.get("execution_type"),
                "execution_status": e.get("execution_status"),
                "duration": e.get("duration"),
                "create_time": e.get("create_time"),
            }
            for e in executions
        ]

        return {
            "range_days": days,
            "kpi": {
                "projects": int(project_total or 0),
                "scripts": int(script_total or 0),
                "test_cases": int(case_total or 0),
                "requirements": int(requirement_total or 0),
                "bugs_open": int(bug_open or 0),
                "executions": exec_stats,
            },
            "execution_trend": trend,
            "bug_status": bug_status,
            "recent_executions": recent_executions,
        }

