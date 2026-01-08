"""
项目仓储

处理项目相关的数据库操作
"""


# noqa  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2xaU1dnPT06YTU0YzE2M2M=

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.repositories.base import BaseRepository
from app.models.project import Project
from app.models.folder import Folder
from app.models.test_case import TestCase
# noqa  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2xaU1dnPT06YTU0YzE2M2M=


class ProjectRepository(BaseRepository[Project]):
    """
    项目仓储类
    
    提供项目相关的数据库操作
    """
    
    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)
    
    async def get_by_identifier(self, identifier: str) -> Optional[Project]:
        """
        根据标识符获取项目
        
        Args:
            identifier: 项目标识符，如 PR-1234
            
        Returns:
            Optional[Project]: 项目实例或 None
        """
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.teams))
            .where(Project.identifier == identifier)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_with_relations(self, id: UUID) -> Optional[Project]:
        """
        根据 ID 获取项目（包含关联数据）
        
        Args:
            id: 项目 ID
            
        Returns:
            Optional[Project]: 项目实例或 None
        """
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.teams))
            .options(selectinload(Project.creator))
            .where(Project.id == id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_with_counts(
        self,
        offset: int = 0,
        limit: int = 30,
    ) -> list[dict]:
        """
        获取所有项目及其统计信息
        
        Args:
            offset: 偏移量
            limit: 限制数量
            
        Returns:
            list[dict]: 项目列表及统计信息
        """
        result = await self.session.execute(
            select(Project)
            .options(selectinload(Project.teams))
            .options(selectinload(Project.creator))
            .offset(offset)
            .limit(limit)
            .order_by(Project.created_at.desc())
        )
        projects = result.scalars().all()
        
        project_data = []
        for project in projects:
            # 获取测试用例数量
            tc_count = await self.session.execute(
                select(func.count()).select_from(TestCase)
                .where(TestCase.project_id == project.id)
            )
            # 获取文件夹数量
            folder_count = await self.session.execute(
                select(func.count()).select_from(Folder)
                .where(Folder.project_id == project.id)
            )
            
            project_data.append({
                "project": project,
                "test_cases_count": tc_count.scalar_one(),
                "folders_count": folder_count.scalar_one(),
            })
# type: ignore  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2xaU1dnPT06YTU0YzE2M2M=
        
        return project_data
    
    async def get_next_sequence(self) -> int:
        """
        获取下一个项目序号
        
        Returns:
            int: 下一个序号
        """
        result = await self.session.execute(
            select(func.count()).select_from(Project)
        )
        count = result.scalar_one()
        return count + 1
    
    async def identifier_exists(self, identifier: str) -> bool:
        """
        检查标识符是否已存在
        
        Args:
            identifier: 项目标识符
            
        Returns:
            bool: 是否存在
        """
        result = await self.session.execute(
            select(func.count()).select_from(Project)
            .where(Project.identifier == identifier)
        )
        return result.scalar_one() > 0

# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2xaU1dnPT06YTU0YzE2M2M=
