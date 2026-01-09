"""
缺陷分析DAO
"""
from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from module_testing.entity.do.defect_analysis_do import DefectAnalysisDO
from utils.log_util import logger


class DefectAnalysisDAO:
    """缺陷分析数据访问对象"""

    async def insert(self, db: AsyncSession, analysis: DefectAnalysisDO) -> DefectAnalysisDO:
        """插入缺陷分析"""
        db.add(analysis)
        await db.commit()
        await db.refresh(analysis)
        return analysis

    async def get_by_id(self, db: AsyncSession, analysis_id: int) -> Optional[DefectAnalysisDO]:
        """根据ID获取缺陷分析"""
        result = await db.execute(
            select(DefectAnalysisDO).where(DefectAnalysisDO.analysis_id == analysis_id)
        )
        return result.scalar_one_or_none()

    async def delete_by_id(self, db: AsyncSession, analysis_id: int) -> bool:
        """根据ID删除缺陷分析"""
        analysis = await self.get_by_id(db, analysis_id)
        if analysis:
            await db.delete(analysis)
            await db.commit()
            return True
        return False

    async def query_with_pagination(
        self,
        db: AsyncSession,
        conditions: List,
        page_num: int = 1,
        page_size: int = 10
    ) -> Tuple[List[DefectAnalysisDO], int]:
        """分页查询"""
        # 构建查询
        query = select(DefectAnalysisDO)
        if conditions:
            query = query.where(and_(*conditions))

        # 总数
        count_query = select(func.count()).select_from(DefectAnalysisDO)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # 分页
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        query = query.order_by(DefectAnalysisDO.create_time.desc())

        result = await db.execute(query)
        records = result.scalars().all()

        return records, total

