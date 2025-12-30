"""
测试项目DAO - 数据访问层
"""
from typing import Optional

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.project_do import TestProject
from module_testing.entity.vo.project_vo import ProjectPageQueryModel


class ProjectDAO:
    """测试项目数据访问对象"""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, project_id: int) -> Optional[TestProject]:
        """根据ID获取项目"""
        result = await db.execute(
            select(TestProject).where(
                and_(
                    TestProject.project_id == project_id,
                    TestProject.del_flag == '0'
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, project_name: str) -> Optional[TestProject]:
        """根据名称获取项目"""
        result = await db.execute(
            select(TestProject).where(
                and_(
                    TestProject.project_name == project_name,
                    TestProject.del_flag == '0'
                )
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        query: ProjectPageQueryModel,
        is_page: bool = True
    ) -> tuple[list[TestProject], int]:
        """获取项目列表"""
        # 构建查询条件
        conditions = [TestProject.del_flag == '0']
        
        if query.project_name:
            conditions.append(TestProject.project_name.like(f'%{query.project_name}%'))
        if query.project_type:
            conditions.append(TestProject.project_type == query.project_type)
        if query.status:
            conditions.append(TestProject.status == query.status)
        if query.begin_time:
            conditions.append(TestProject.create_time >= query.begin_time)
        if query.end_time:
            conditions.append(TestProject.create_time <= query.end_time)
        
        # 查询总数
        count_query = select(func.count(TestProject.project_id)).where(and_(*conditions))
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0
        
        # 查询列表
        list_query = select(TestProject).where(and_(*conditions)).order_by(TestProject.create_time.desc())
        
        if is_page:
            offset = (query.page_num - 1) * query.page_size
            list_query = list_query.offset(offset).limit(query.page_size)
        
        result = await db.execute(list_query)
        projects = result.scalars().all()
        
        return list(projects), total
    
    @staticmethod
    async def get_all(db: AsyncSession, status: Optional[str] = None) -> list[TestProject]:
        """获取所有项目"""
        conditions = [TestProject.del_flag == '0']
        if status:
            conditions.append(TestProject.status == status)
        
        result = await db.execute(
            select(TestProject).where(and_(*conditions)).order_by(TestProject.project_name)
        )
        return list(result.scalars().all())
    
    @staticmethod
    async def create(db: AsyncSession, project: TestProject) -> TestProject:
        """创建项目"""
        db.add(project)
        await db.flush()
        await db.refresh(project)
        return project
    
    @staticmethod
    async def update_by_id(db: AsyncSession, project_id: int, **kwargs) -> bool:
        """更新项目"""
        result = await db.execute(
            update(TestProject)
            .where(TestProject.project_id == project_id)
            .values(**kwargs)
        )
        return result.rowcount > 0
    
    @staticmethod
    async def delete_by_ids(db: AsyncSession, project_ids: list[int]) -> int:
        """批量软删除项目"""
        result = await db.execute(
            update(TestProject)
            .where(TestProject.project_id.in_(project_ids))
            .values(del_flag='2')
        )
        return result.rowcount
    
    @staticmethod
    async def check_name_unique(
        db: AsyncSession, 
        project_name: str, 
        project_id: Optional[int] = None
    ) -> bool:
        """检查项目名称是否唯一"""
        conditions = [
            TestProject.project_name == project_name,
            TestProject.del_flag == '0'
        ]
        if project_id:
            conditions.append(TestProject.project_id != project_id)
        
        result = await db.execute(
            select(func.count(TestProject.project_id)).where(and_(*conditions))
        )
        count = result.scalar() or 0
        return count == 0

