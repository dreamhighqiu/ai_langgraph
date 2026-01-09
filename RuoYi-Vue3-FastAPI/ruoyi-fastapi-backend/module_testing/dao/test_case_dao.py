"""
测试用例数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.test_case_do import TestCaseDO
from utils.log_util import logger


class TestCaseDao:
    """测试用例DAO"""

    @staticmethod
    async def insert(db: AsyncSession, test_case: TestCaseDO) -> TestCaseDO:
        """插入测试用例"""
        db.add(test_case)
        await db.flush()
        await db.refresh(test_case)
        return test_case

    @staticmethod
    async def update(db: AsyncSession, test_case: TestCaseDO) -> TestCaseDO:
        """更新测试用例"""
        await db.flush()
        await db.refresh(test_case)
        return test_case

    @staticmethod
    async def delete(db: AsyncSession, case_id: int) -> bool:
        """删除测试用例"""
        result = await db.execute(
            select(TestCaseDO).where(TestCaseDO.case_id == case_id)
        )
        test_case = result.scalar_one_or_none()
        if test_case:
            await db.delete(test_case)
            await db.flush()
            return True
        return False

    @staticmethod
    async def select_by_id(db: AsyncSession, case_id: int) -> Optional[TestCaseDO]:
        """根据ID查询测试用例"""
        result = await db.execute(
            select(TestCaseDO).where(TestCaseDO.case_id == case_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_by_identifier(db: AsyncSession, identifier: str) -> Optional[TestCaseDO]:
        """根据标识符查询测试用例"""
        result = await db.execute(
            select(TestCaseDO).where(TestCaseDO.case_identifier == identifier)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_list(
        db: AsyncSession,
        query_params: Dict[str, Any],
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple[List[TestCaseDO], int]:
        """分页查询测试用例列表"""
        # 构建查询条件
        conditions = []
        
        if query_params.get('project_id'):
            conditions.append(TestCaseDO.project_id == query_params['project_id'])
        
        if query_params.get('folder_id'):
            conditions.append(TestCaseDO.folder_id == query_params['folder_id'])
        
        if query_params.get('case_name'):
            conditions.append(TestCaseDO.case_name.like(f"%{query_params['case_name']}%"))
        
        if query_params.get('case_type'):
            conditions.append(TestCaseDO.case_type == query_params['case_type'])
        
        if query_params.get('status'):
            conditions.append(TestCaseDO.status == query_params['status'])
        
        if query_params.get('priority'):
            conditions.append(TestCaseDO.priority == query_params['priority'])
        
        if query_params.get('tags'):
            tag_list = query_params['tags'].split(',')
            tag_conditions = [TestCaseDO.tags.like(f"%{tag}%") for tag in tag_list]
            conditions.append(or_(*tag_conditions))
        
        if query_params.get('create_by'):
            conditions.append(TestCaseDO.create_by == query_params['create_by'])

        # 查询总数
        count_query = select(func.count()).select_from(TestCaseDO)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total = await db.scalar(count_query)

        # 分页查询
        query = select(TestCaseDO)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(TestCaseDO.create_time.desc())
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        records = result.scalars().all()

        return list(records), total or 0

    @staticmethod
    async def count_by_project(db: AsyncSession, project_id: int) -> int:
        """统计项目下的测试用例数量"""
        result = await db.execute(
            select(func.count()).select_from(TestCaseDO).where(
                TestCaseDO.project_id == project_id
            )
        )
        return result.scalar() or 0

    @staticmethod
    async def get_next_identifier(db: AsyncSession, project_id: int) -> str:
        """生成下一个用例标识符"""
        result = await db.execute(
            select(func.count()).select_from(TestCaseDO).where(
                TestCaseDO.project_id == project_id
            )
        )
        count = result.scalar() or 0
        return f"TC-{project_id}-{count + 1:04d}"

    @staticmethod
    async def batch_insert(db: AsyncSession, test_cases: List[TestCaseDO]) -> List[TestCaseDO]:
        """批量插入测试用例"""
        db.add_all(test_cases)
        await db.flush()
        for test_case in test_cases:
            await db.refresh(test_case)
        return test_cases

    @staticmethod
    async def update_execution_stats(
        db: AsyncSession,
        case_id: int,
        execution_status: str
    ) -> bool:
        """更新执行统计"""
        test_case = await TestCaseDao.select_by_id(db, case_id)
        if not test_case:
            return False
        
        test_case.execution_count += 1
        test_case.execution_status = execution_status
        
        if execution_status == 'passed':
            test_case.pass_count += 1
        elif execution_status == 'failed':
            test_case.fail_count += 1
        
        await db.flush()
        return True

    @staticmethod
    async def count_by_status(db: AsyncSession, project_id: int) -> dict:
        """按状态统计测试用例数量"""
        result = await db.execute(
            select(TestCaseDO.status, func.count()).select_from(TestCaseDO)
            .where(TestCaseDO.project_id == project_id)
            .group_by(TestCaseDO.status)
        )
        return {row[0]: row[1] for row in result.all()}

    @staticmethod
    async def count_by_priority(db: AsyncSession, project_id: int) -> dict:
        """按优先级统计测试用例数量"""
        result = await db.execute(
            select(TestCaseDO.priority, func.count()).select_from(TestCaseDO)
            .where(TestCaseDO.project_id == project_id)
            .group_by(TestCaseDO.priority)
        )
        return {row[0]: row[1] for row in result.all()}

