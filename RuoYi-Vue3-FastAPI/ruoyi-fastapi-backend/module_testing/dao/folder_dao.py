"""
文件夹数据访问层
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, func, and_, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.folder_do import FolderDO
from utils.log_util import logger


class FolderDao:
    """文件夹DAO"""

    @staticmethod
    async def insert(db: AsyncSession, folder: FolderDO) -> FolderDO:
        """插入文件夹"""
        db.add(folder)
        await db.flush()
        await db.refresh(folder)
        return folder

    @staticmethod
    async def update(db: AsyncSession, folder: FolderDO) -> FolderDO:
        """更新文件夹"""
        await db.flush()
        await db.refresh(folder)
        return folder

    @staticmethod
    async def delete(db: AsyncSession, folder_id: int) -> bool:
        """删除文件夹"""
        result = await db.execute(
            select(FolderDO).where(FolderDO.folder_id == folder_id)
        )
        folder = result.scalar_one_or_none()
        if folder:
            await db.delete(folder)
            await db.flush()
            return True
        return False

    @staticmethod
    async def delete_by_project(db: AsyncSession, project_id: int) -> int:
        """删除项目下所有文件夹"""
        result = await db.execute(
            delete(FolderDO).where(FolderDO.project_id == project_id)
        )
        await db.flush()
        return result.rowcount

    @staticmethod
    async def select_by_id(db: AsyncSession, folder_id: int) -> Optional[FolderDO]:
        """根据ID查询文件夹"""
        result = await db.execute(
            select(FolderDO).where(FolderDO.folder_id == folder_id)
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_by_project_and_name(
        db: AsyncSession, 
        project_id: int, 
        folder_name: str,
        parent_id: Optional[int] = None
    ) -> Optional[FolderDO]:
        """根据项目ID和文件夹名称查询"""
        conditions = [
            FolderDO.project_id == project_id,
            FolderDO.folder_name == folder_name
        ]
        if parent_id is not None:
            conditions.append(FolderDO.parent_id == parent_id)
        else:
            conditions.append(FolderDO.parent_id.is_(None))
            
        result = await db.execute(
            select(FolderDO).where(and_(*conditions))
        )
        return result.scalar_one_or_none()

    @staticmethod
    async def select_children(db: AsyncSession, parent_id: Optional[int], project_id: int) -> List[FolderDO]:
        """查询子文件夹"""
        conditions = [FolderDO.project_id == project_id]
        if parent_id is not None:
            conditions.append(FolderDO.parent_id == parent_id)
        else:
            conditions.append(FolderDO.parent_id.is_(None))
            
        result = await db.execute(
            select(FolderDO).where(and_(*conditions)).order_by(FolderDO.sort_order, FolderDO.folder_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def select_all_by_project(db: AsyncSession, project_id: int) -> List[FolderDO]:
        """查询项目下所有文件夹"""
        result = await db.execute(
            select(FolderDO).where(FolderDO.project_id == project_id)
            .order_by(FolderDO.sort_order, FolderDO.folder_id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def select_list(
        db: AsyncSession,
        query_params: Dict[str, Any],
        page_num: int = 1,
        page_size: int = 10
    ) -> tuple[List[FolderDO], int]:
        """分页查询文件夹列表"""
        conditions = []
        
        if query_params.get('project_id'):
            conditions.append(FolderDO.project_id == query_params['project_id'])
        
        if query_params.get('parent_id') is not None:
            if query_params['parent_id'] == 0:
                conditions.append(FolderDO.parent_id.is_(None))
            else:
                conditions.append(FolderDO.parent_id == query_params['parent_id'])
        
        if query_params.get('folder_name'):
            conditions.append(FolderDO.folder_name.like(f"%{query_params['folder_name']}%"))
        
        if query_params.get('status'):
            conditions.append(FolderDO.status == query_params['status'])

        # 查询总数
        count_query = select(func.count()).select_from(FolderDO)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        total = await db.scalar(count_query)

        # 分页查询
        query = select(FolderDO)
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(FolderDO.sort_order, FolderDO.folder_id)
        query = query.offset((page_num - 1) * page_size).limit(page_size)
        
        result = await db.execute(query)
        records = result.scalars().all()

        return list(records), total or 0

    @staticmethod
    async def count_by_parent(db: AsyncSession, parent_id: Optional[int], project_id: int) -> int:
        """统计子文件夹数量"""
        conditions = [FolderDO.project_id == project_id]
        if parent_id is not None:
            conditions.append(FolderDO.parent_id == parent_id)
        else:
            conditions.append(FolderDO.parent_id.is_(None))
            
        result = await db.execute(
            select(func.count()).select_from(FolderDO).where(and_(*conditions))
        )
        return result.scalar() or 0

    @staticmethod
    async def update_child_count(db: AsyncSession, folder_id: int, count: int) -> None:
        """更新子文件夹数量"""
        await db.execute(
            update(FolderDO)
            .where(FolderDO.folder_id == folder_id)
            .values(child_count=count)
        )
        await db.flush()

    @staticmethod
    async def update_case_count(db: AsyncSession, folder_id: int, count: int) -> None:
        """更新测试用例数量"""
        await db.execute(
            update(FolderDO)
            .where(FolderDO.folder_id == folder_id)
            .values(case_count=count)
        )
        await db.flush()

    @staticmethod
    async def increment_case_count(db: AsyncSession, folder_id: int, delta: int = 1) -> None:
        """增加测试用例数量"""
        await db.execute(
            update(FolderDO)
            .where(FolderDO.folder_id == folder_id)
            .values(case_count=FolderDO.case_count + delta)
        )
        await db.flush()

    @staticmethod
    async def has_children(db: AsyncSession, folder_id: int) -> bool:
        """检查是否有子文件夹"""
        result = await db.execute(
            select(func.count()).select_from(FolderDO).where(FolderDO.parent_id == folder_id)
        )
        return (result.scalar() or 0) > 0

    @staticmethod
    async def get_folder_path(db: AsyncSession, folder_id: int) -> str:
        """获取文件夹路径"""
        path_parts = []
        current_id = folder_id
        
        while current_id is not None:
            folder = await FolderDao.select_by_id(db, current_id)
            if folder:
                path_parts.insert(0, folder.folder_name)
                current_id = folder.parent_id
            else:
                break
        
        return '/' + '/'.join(path_parts) if path_parts else '/'

