"""
需求分析数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.requirement_analysis_do import RequirementAnalysisDO
from utils.log_util import logger


class RequirementAnalysisDao:
    """需求分析DAO"""

    @staticmethod
    async def insert(db: AsyncSession, requirement: RequirementAnalysisDO) -> RequirementAnalysisDO:
        """插入需求分析"""
        db.add(requirement)
        await db.flush()
        await db.refresh(requirement)
        return requirement

    @staticmethod
    async def update(db: AsyncSession, requirement: RequirementAnalysisDO) -> RequirementAnalysisDO:
        """更新需求分析"""
        await db.flush()
        await db.refresh(requirement)
        return requirement

    @staticmethod
    async def delete(db: AsyncSession, requirement_id: int) -> bool:
        """删除需求分析"""
        result = await db.execute(
            select(RequirementAnalysisDO).where(RequirementAnalysisDO.requirement_id == requirement_id)
        )
        requirement = result.scalar_one_or_none()
        if requirement:
            await db.delete(requirement)
            await db.flush()
            return True
        return False

    @staticmethod
    async def select_by_id(db: AsyncSession, requirement_id: int) -> Optional[RequirementAnalysisDO]:
        """根据ID查询需求分析"""
        result = await db.execute(
            select(RequirementAnalysisDO).where(RequirementAnalysisDO.requirement_id == requirement_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_by_identifier(db: AsyncSession, identifier: str) -> Optional[RequirementAnalysisDO]:
        """根据标识符查询需求分析"""
        result = await db.execute(
            select(RequirementAnalysisDO).where(RequirementAnalysisDO.requirement_identifier == identifier)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_list(
        db: AsyncSession,
        query_params: Dict[str, Any],
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple[List[RequirementAnalysisDO], int]:
        """分页查询需求分析列表"""
        # 构建查询条件
        conditions = []
        
        if query_params.get('project_id'):
            conditions.append(RequirementAnalysisDO.project_id == query_params['project_id'])
        
        if query_params.get('requirement_name'):
            conditions.append(RequirementAnalysisDO.requirement_name.like(f"%{query_params['requirement_name']}%"))
        
        if query_params.get('requirement_type'):
            conditions.append(RequirementAnalysisDO.requirement_type == query_params['requirement_type'])
        
        if query_params.get('priority'):
            conditions.append(RequirementAnalysisDO.priority == query_params['priority'])
        
        if query_params.get('status'):
            conditions.append(RequirementAnalysisDO.status == query_params['status'])
        
        if query_params.get('module'):
            conditions.append(RequirementAnalysisDO.module.like(f"%{query_params['module']}%"))
        
        if query_params.get('created_by'):
            conditions.append(RequirementAnalysisDO.created_by == query_params['created_by'])

        # 查询总数
        count_query = select(func.count()).select_from(RequirementAnalysisDO)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total = await db.scalar(count_query)

        # 分页查询
        query = select(RequirementAnalysisDO)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(RequirementAnalysisDO.create_time.desc())
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        records = result.scalars().all()

        return list(records), total or 0

    @staticmethod
    async def count_by_project(db: AsyncSession, project_id: int) -> int:
        """统计项目下的需求数量"""
        result = await db.execute(
            select(func.count()).select_from(RequirementAnalysisDO).where(
                RequirementAnalysisDO.project_id == project_id
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_next_identifier(db: AsyncSession, project_id: int) -> str:
        """生成下一个需求标识符"""
        result = await db.execute(
            select(func.count()).select_from(RequirementAnalysisDO).where(
                RequirementAnalysisDO.project_id == project_id
            )
        )
        count = result.scalar() or 0
        return f"REQ-{project_id}-{count + 1:04d}"

    @staticmethod
    async def batch_insert(db: AsyncSession, requirements: List[RequirementAnalysisDO]) -> List[RequirementAnalysisDO]:
        """批量插入需求分析"""
        db.add_all(requirements)
        await db.flush()
        for requirement in requirements:
            await db.refresh(requirement)
        return requirements

    @staticmethod
    async def count_by_status(db: AsyncSession, project_id: int, status: str) -> int:
        """统计指定状态的需求数量"""
        result = await db.execute(
            select(func.count()).select_from(RequirementAnalysisDO).where(
                and_(
                    RequirementAnalysisDO.project_id == project_id,
                    RequirementAnalysisDO.status == status
                )
            )
        )
        return result.scalar() or 0

