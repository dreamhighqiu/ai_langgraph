"""
缺陷报告数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.bug_report_do import BugReportDO
from utils.log_util import logger


class BugReportDao:
    """缺陷报告DAO"""

    @staticmethod
    async def insert(db: AsyncSession, bug_report: BugReportDO) -> BugReportDO:
        """插入缺陷报告"""
        db.add(bug_report)
        await db.flush()
        await db.refresh(bug_report)
        return bug_report

    @staticmethod
    async def update(db: AsyncSession, bug_report: BugReportDO) -> BugReportDO:
        """更新缺陷报告"""
        await db.flush()
        await db.refresh(bug_report)
        return bug_report

    @staticmethod
    async def delete(db: AsyncSession, bug_id: int) -> bool:
        """删除缺陷报告"""
        result = await db.execute(
            select(BugReportDO).where(BugReportDO.bug_id == bug_id)
        )
        bug_report = result.scalar_one_or_none()
        if bug_report:
            await db.delete(bug_report)
            await db.flush()
            return True
        return False

    @staticmethod
    async def select_by_id(db: AsyncSession, bug_id: int) -> Optional[BugReportDO]:
        """根据ID查询缺陷报告"""
        result = await db.execute(
            select(BugReportDO).where(BugReportDO.bug_id == bug_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_by_identifier(db: AsyncSession, identifier: str) -> Optional[BugReportDO]:
        """根据标识符查询缺陷报告"""
        result = await db.execute(
            select(BugReportDO).where(BugReportDO.bug_identifier == identifier)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_list(
        db: AsyncSession,
        query_params: Dict[str, Any],
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple[List[BugReportDO], int]:
        """分页查询缺陷报告列表"""
        # 构建查询条件
        conditions = []
        
        if query_params.get('project_id'):
            conditions.append(BugReportDO.project_id == query_params['project_id'])
        
        if query_params.get('bug_title'):
            conditions.append(BugReportDO.bug_title.like(f"%{query_params['bug_title']}%"))
        
        if query_params.get('severity'):
            conditions.append(BugReportDO.severity == query_params['severity'])
        
        if query_params.get('priority'):
            conditions.append(BugReportDO.priority == query_params['priority'])
        
        if query_params.get('status'):
            conditions.append(BugReportDO.status == query_params['status'])
        
        if query_params.get('bug_type'):
            conditions.append(BugReportDO.bug_type == query_params['bug_type'])
        
        if query_params.get('assigned_to'):
            conditions.append(BugReportDO.assigned_to == query_params['assigned_to'])
        
        if query_params.get('reporter'):
            conditions.append(BugReportDO.reporter == query_params['reporter'])

        # 查询总数
        count_query = select(func.count()).select_from(BugReportDO)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total = await db.scalar(count_query)

        # 分页查询
        query = select(BugReportDO)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(BugReportDO.create_time.desc())
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        records = result.scalars().all()

        return list(records), total or 0

    @staticmethod
    async def count_by_project(db: AsyncSession, project_id: int) -> int:
        """统计项目下的缺陷数量"""
        result = await db.execute(
            select(func.count()).select_from(BugReportDO).where(
                BugReportDO.project_id == project_id
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_next_identifier(db: AsyncSession, project_id: int) -> str:
        """生成下一个缺陷标识符"""
        result = await db.execute(
            select(func.count()).select_from(BugReportDO).where(
                BugReportDO.project_id == project_id
            )
        )
        count = result.scalar() or 0
        return f"BUG-{project_id}-{count + 1:04d}"

    @staticmethod
    async def batch_insert(db: AsyncSession, bug_reports: List[BugReportDO]) -> List[BugReportDO]:
        """批量插入缺陷报告"""
        db.add_all(bug_reports)
        await db.flush()
        for bug_report in bug_reports:
            await db.refresh(bug_report)
        return bug_reports

    @staticmethod
    async def count_by_status(db: AsyncSession, project_id: int, status: str) -> int:
        """统计指定状态的缺陷数量"""
        result = await db.execute(
            select(func.count()).select_from(BugReportDO).where(
                and_(
                    BugReportDO.project_id == project_id,
                    BugReportDO.status == status
                )
            )
        )
        return result.scalar() or 0

