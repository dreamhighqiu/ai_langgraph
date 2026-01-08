"""
文件夹服务

处理文件夹相关的业务逻辑
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.folder import Folder
from app.repositories.folder_repo import FolderRepository
from app.repositories.project_repo import ProjectRepository
from app.schemas.folder import FolderCreate, FolderUpdate, FolderMove, FolderInfo, FolderLinks
from app.utils.exceptions import NotFoundException, BadRequestException
from app.config.settings import settings


class FolderService:
    """
    文件夹服务类
    
    处理文件夹相关的业务逻辑
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = FolderRepository(session)
        self.project_repo = ProjectRepository(session)
    
    async def _get_project_by_identifier(self, identifier: str):
        """获取项目，不存在则抛出异常"""
        project = await self.project_repo.get_by_identifier(identifier)
        if not project:
            raise NotFoundException(resource_type="项目", resource_id=identifier)
        return project
    
    async def _folder_to_info(self, folder: Folder, project_identifier: str) -> FolderInfo:
        """
        将文件夹模型转换为响应模型

        参考 BrowserStack API 响应格式:
        https://www.browserstack.com/docs/test-management/api-reference/folders

        显示格式: 直接用例数(总用例数)
        """
        data = await self.repo.get_with_counts(folder.id)

        return FolderInfo(
            id=folder.id,
            name=folder.name,
            description=folder.description,
            parent_id=folder.parent_id,
            direct_cases_count=data["direct_cases_count"] if data else 0,
            cases_count=data["cases_count"] if data else 0,
            sub_folders_count=data["sub_folders_count"] if data else 0,
            links=FolderLinks(
                sub_folders=f"{settings.api_prefix}/projects/{project_identifier}/folders/{folder.id}/sub-folders",
            ),
        )
    
    async def get_folders(
        self,
        project_identifier: str,
        offset: int = 0,
        limit: int = 30,
    ) -> tuple[list[FolderInfo], int]:
        """获取项目下的所有文件夹列表"""
        project = await self._get_project_by_identifier(project_identifier)

        folders = await self.repo.get_by_project(project.id, offset, limit)
        total = await self.repo.count_by_project(project.id)
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFCaFRBPT06YjY4N2JjMzM=

        result = []
        for folder in folders:
            info = await self._folder_to_info(folder, project_identifier)
            result.append(info)

        return result, total

    async def get_root_folders(
        self,
        project_identifier: str,
        offset: int = 0,
        limit: int = 30,
    ) -> tuple[list[FolderInfo], int]:
        """获取项目下的根文件夹列表（parent_id为null）"""
        project = await self._get_project_by_identifier(project_identifier)

        folders = await self.repo.get_root_folders(project.id, offset, limit)

        # 计算根文件夹总数
        from sqlalchemy import func, select
        from app.models.folder import Folder as FolderModel
        count_result = await self.session.execute(
            select(func.count()).select_from(FolderModel)
            .where(FolderModel.project_id == project.id)
            .where(FolderModel.parent_id.is_(None))
        )
        total = count_result.scalar_one()

        result = []
        for folder in folders:
            info = await self._folder_to_info(folder, project_identifier)
            result.append(info)
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFCaFRBPT06YjY4N2JjMzM=

        return result, total

    async def get_folder(
        self,
        project_identifier: str,
        folder_id: UUID,
    ) -> FolderInfo:
        """获取文件夹详情"""
        project = await self._get_project_by_identifier(project_identifier)
        
        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))
        
        return await self._folder_to_info(folder, project_identifier)
    
    async def get_sub_folders(
        self,
        project_identifier: str,
        folder_id: UUID,
        offset: int = 0,
        limit: int = 30,
    ) -> tuple[list[FolderInfo], int]:
        """获取子文件夹列表"""
        project = await self._get_project_by_identifier(project_identifier)
        
        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))
        
        sub_folders = await self.repo.get_sub_folders(folder_id, offset, limit)
        
        result = []
        for sub in sub_folders:
            info = await self._folder_to_info(sub, project_identifier)
            result.append(info)
        
        # 简化：子文件夹总数
        from sqlalchemy import func, select
        from app.models.folder import Folder as FolderModel
        count_result = await self.session.execute(
            select(func.count()).select_from(FolderModel)
            .where(FolderModel.parent_id == folder_id)
        )
        total = count_result.scalar_one()
        
        return result, total
    
    async def create_folder(
        self,
        project_identifier: str,
        data: FolderCreate,
    ) -> FolderInfo:
        """创建文件夹"""
        project = await self._get_project_by_identifier(project_identifier)
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFCaFRBPT06YjY4N2JjMzM=
        
        # 验证父文件夹
        if data.parent_id:
            parent = await self.repo.get_by_id(data.parent_id)
            if not parent or parent.project_id != project.id:
                raise BadRequestException("父文件夹不存在或不属于该项目")
        
        folder = await self.repo.create(
            project_id=project.id,
            parent_id=data.parent_id,
            name=data.name,
            description=data.description,
        )
        
        return await self._folder_to_info(folder, project_identifier)
    
    async def update_folder(
        self,
        project_identifier: str,
        folder_id: UUID,
        data: FolderUpdate,
    ) -> FolderInfo:
        """更新文件夹"""
        project = await self._get_project_by_identifier(project_identifier)
        
        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))
        
        folder = await self.repo.update(
            folder,
            name=data.name,
            description=data.description,
        )
        
        return await self._folder_to_info(folder, project_identifier)
    
    async def delete_folder(
        self,
        project_identifier: str,
        folder_id: UUID,
    ) -> str:
        """删除文件夹"""
        project = await self._get_project_by_identifier(project_identifier)
        
        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))
# noqa  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2WTFCaFRBPT06YjY4N2JjMzM=
        
        await self.repo.delete(folder)
        return f"文件夹 {folder_id} 已成功删除"

    async def move_folder(
        self,
        project_identifier: str,
        folder_id: UUID,
        data: FolderMove,
    ) -> FolderInfo:
        """
        移动文件夹到新位置

        参考: https://www.browserstack.com/docs/test-management/api-reference/folders#move-a-folder

        Args:
            project_identifier: 项目标识符
            folder_id: 文件夹 ID
            data: 移动请求数据 (parent_id: 目标父文件夹 ID，为 null 则移动到根目录)

        Returns:
            FolderInfo: 移动后的文件夹信息
        """
        project = await self._get_project_by_identifier(project_identifier)

        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))

        # 验证目标父文件夹
        if data.parent_id:
            dest = await self.repo.get_by_id(data.parent_id)
            if not dest or dest.project_id != project.id:
                raise BadRequestException("目标父文件夹不存在或不属于该项目")

            # 检查是否移动到自己
            if data.parent_id == folder_id:
                raise BadRequestException("不能将文件夹移动到自身")

            # 检查是否是子文件夹（防止循环引用）
            current = dest
            while current.parent_id:
                if current.parent_id == folder_id:
                    raise BadRequestException("不能将文件夹移动到其子文件夹中")
                current = await self.repo.get_by_id(current.parent_id)

        folder = await self.repo.move_folder(folder, data.parent_id)
        return await self._folder_to_info(folder, project_identifier)

    async def copy_folder(
        self,
        project_identifier: str,
        folder_id: UUID,
    ) -> FolderInfo:
        """
        复制文件夹及其所有内容

        Args:
            project_identifier: 项目标识符
            folder_id: 源文件夹 ID

        Returns:
            FolderInfo: 新创建的文件夹信息
        """
        project = await self._get_project_by_identifier(project_identifier)

        folder = await self.repo.get_by_id(folder_id)
        if not folder or folder.project_id != project.id:
            raise NotFoundException(resource_type="文件夹", resource_id=str(folder_id))

        # 复制文件夹（递归复制）
        new_folder = await self.repo.copy_folder(folder, f"{folder.name} (副本)")

        return await self._folder_to_info(new_folder, project_identifier)

