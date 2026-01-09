"""
文件夹服务层
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.folder_dao import FolderDao
from module_testing.entity.do.folder_do import FolderDO
from module_testing.entity.vo.folder_vo import (
    FolderCreateVO, FolderUpdateVO, FolderQueryVO, FolderTreeNodeVO
)
from utils.log_util import logger


class FolderService:
    """文件夹服务"""

    def __init__(self):
        self.folder_dao = FolderDao()

    async def create_folder(
        self, 
        db: AsyncSession, 
        folder_vo: FolderCreateVO,
        user_name: str
    ) -> FolderDO:
        """创建文件夹"""
        try:
            # 验证项目ID
            if not folder_vo.project_id or folder_vo.project_id <= 0:
                raise ValueError("项目ID无效，请先选择项目")
            
            # 验证文件夹名称
            if not folder_vo.folder_name or not folder_vo.folder_name.strip():
                raise ValueError("文件夹名称不能为空")
            
            # 如果指定了父文件夹，验证父文件夹是否存在且属于同一项目
            if folder_vo.parent_id:
                parent_folder = await self.folder_dao.select_by_id(db, folder_vo.parent_id)
                if not parent_folder:
                    raise ValueError(f"父文件夹不存在: {folder_vo.parent_id}")
                if parent_folder.project_id != folder_vo.project_id:
                    raise ValueError("父文件夹不属于当前项目")
            
            # 检查同级目录下是否有同名文件夹
            existing = await self.folder_dao.select_by_project_and_name(
                db, folder_vo.project_id, folder_vo.folder_name.strip(), folder_vo.parent_id
            )
            if existing:
                raise ValueError(f"同级目录下已存在同名文件夹: {folder_vo.folder_name}")
            
            # 创建文件夹对象
            folder_do = FolderDO(
                project_id=folder_vo.project_id,
                parent_id=folder_vo.parent_id if folder_vo.parent_id else None,
                folder_name=folder_vo.folder_name.strip(),
                description=folder_vo.description,
                sort_order=folder_vo.sort_order or 0,
                case_count=0,
                child_count=0,
                status='0',
                create_by=user_name,
                create_time=datetime.now(),
                remark=folder_vo.remark
            )
            
            # 保存到数据库
            result = await self.folder_dao.insert(db, folder_do)
            
            # 更新文件夹路径
            folder_path = await self.folder_dao.get_folder_path(db, result.folder_id)
            result.folder_path = folder_path
            await self.folder_dao.update(db, result)
            
            # 更新父文件夹的子文件夹数量
            if folder_vo.parent_id:
                child_count = await self.folder_dao.count_by_parent(db, folder_vo.parent_id, folder_vo.project_id)
                await self.folder_dao.update_child_count(db, folder_vo.parent_id, child_count)
            
            await db.commit()
            
            logger.info(f"创建文件夹成功: {folder_vo.folder_name} (项目ID: {folder_vo.project_id})")
            return result
            
        except ValueError as e:
            await db.rollback()
            logger.warning(f"创建文件夹验证失败: {str(e)}")
            raise
        except Exception as e:
            await db.rollback()
            logger.error(f"创建文件夹失败: {str(e)}", exc_info=True)
            raise

    async def update_folder(
        self,
        db: AsyncSession,
        folder_id: int,
        folder_vo: FolderUpdateVO,
        user_name: str
    ) -> FolderDO:
        """更新文件夹"""
        try:
            folder = await self.folder_dao.select_by_id(db, folder_id)
            if not folder:
                raise ValueError(f"文件夹不存在: {folder_id}")
            
            # 如果修改了名称，检查同级是否有同名
            if folder_vo.folder_name and folder_vo.folder_name != folder.folder_name:
                existing = await self.folder_dao.select_by_project_and_name(
                    db, folder.project_id, folder_vo.folder_name, folder.parent_id
                )
                if existing:
                    raise ValueError(f"同级目录下已存在同名文件夹: {folder_vo.folder_name}")
                folder.folder_name = folder_vo.folder_name
            
            # 更新其他字段
            if folder_vo.description is not None:
                folder.description = folder_vo.description
            if folder_vo.sort_order is not None:
                folder.sort_order = folder_vo.sort_order
            if folder_vo.status is not None:
                folder.status = folder_vo.status
            if folder_vo.remark is not None:
                folder.remark = folder_vo.remark
            
            folder.update_by = user_name
            folder.update_time = datetime.now()
            
            # 更新路径
            folder.folder_path = await self.folder_dao.get_folder_path(db, folder_id)
            
            result = await self.folder_dao.update(db, folder)
            await db.commit()
            
            logger.info(f"更新文件夹成功: {folder_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"更新文件夹失败: {str(e)}")
            raise

    async def delete_folder(self, db: AsyncSession, folder_id: int) -> bool:
        """删除文件夹"""
        try:
            folder = await self.folder_dao.select_by_id(db, folder_id)
            if not folder:
                return False
            
            # 检查是否有子文件夹
            has_children = await self.folder_dao.has_children(db, folder_id)
            if has_children:
                raise ValueError("文件夹下有子文件夹，无法删除")
            
            # 检查是否有测试用例
            if folder.case_count > 0:
                raise ValueError("文件夹下有测试用例，无法删除")
            
            parent_id = folder.parent_id
            project_id = folder.project_id
            
            result = await self.folder_dao.delete(db, folder_id)
            
            # 更新父文件夹的子文件夹数量
            if parent_id:
                child_count = await self.folder_dao.count_by_parent(db, parent_id, project_id)
                await self.folder_dao.update_child_count(db, parent_id, child_count)
            
            await db.commit()
            logger.info(f"删除文件夹成功: {folder_id}")
            return result
            
        except Exception as e:
            await db.rollback()
            logger.error(f"删除文件夹失败: {str(e)}")
            raise

    async def get_folder(self, db: AsyncSession, folder_id: int) -> Optional[FolderDO]:
        """获取文件夹详情"""
        return await self.folder_dao.select_by_id(db, folder_id)

    async def query_folder_list(
        self,
        db: AsyncSession,
        query_vo: FolderQueryVO
    ) -> tuple[List[FolderDO], int]:
        """查询文件夹列表"""
        query_params = query_vo.model_dump(exclude_none=True, exclude={'page_num', 'page_size'})
        return await self.folder_dao.select_list(
            db,
            query_params,
            query_vo.page_num,
            query_vo.page_size
        )

    async def get_folder_tree(self, db: AsyncSession, project_id: int) -> List[Dict[str, Any]]:
        """获取文件夹树"""
        try:
            # 获取所有文件夹
            all_folders = await self.folder_dao.select_all_by_project(db, project_id)
            
            # 如果没有文件夹，返回空列表
            if not all_folders:
                return []
            
            # 构建ID到文件夹的映射
            folder_map = {f.folder_id: f.to_dict() for f in all_folders}
            
            # 构建树结构
            root_folders = []
            for folder in all_folders:
                folder_dict = folder_map.get(folder.folder_id)
                if not folder_dict:
                    continue
                    
                folder_dict['children'] = []
                
                if folder.parent_id is None:
                    root_folders.append(folder_dict)
                else:
                    parent = folder_map.get(folder.parent_id)
                    if parent:
                        if 'children' not in parent:
                            parent['children'] = []
                        parent['children'].append(folder_dict)
            
            return root_folders
        except Exception as e:
            logger.error(f"构建文件夹树失败: {str(e)}", exc_info=True)
            raise ValueError(f"构建文件夹树失败: {str(e)}")

    async def move_folder(
        self,
        db: AsyncSession,
        folder_id: int,
        target_parent_id: Optional[int],
        user_name: str
    ) -> FolderDO:
        """移动文件夹"""
        try:
            folder = await self.folder_dao.select_by_id(db, folder_id)
            if not folder:
                raise ValueError(f"文件夹不存在: {folder_id}")
            
            # 检查目标是否是自己的子文件夹
            if target_parent_id:
                target = await self.folder_dao.select_by_id(db, target_parent_id)
                if not target:
                    raise ValueError(f"目标文件夹不存在: {target_parent_id}")
                if target.project_id != folder.project_id:
                    raise ValueError("不能移动到其他项目")
                
                # 检查目标是否是当前文件夹的子孙
                current_id = target_parent_id
                while current_id:
                    if current_id == folder_id:
                        raise ValueError("不能将文件夹移动到自己的子目录中")
                    parent = await self.folder_dao.select_by_id(db, current_id)
                    current_id = parent.parent_id if parent else None
            
            # 检查目标目录下是否有同名文件夹
            existing = await self.folder_dao.select_by_project_and_name(
                db, folder.project_id, folder.folder_name, target_parent_id
            )
            if existing and existing.folder_id != folder_id:
                raise ValueError(f"目标目录下已存在同名文件夹: {folder.folder_name}")
            
            old_parent_id = folder.parent_id
            folder.parent_id = target_parent_id
            folder.update_by = user_name
            folder.update_time = datetime.now()
            
            # 更新路径
            folder.folder_path = await self.folder_dao.get_folder_path(db, folder_id)
            
            await self.folder_dao.update(db, folder)
            
            # 更新原父文件夹的子文件夹数量
            if old_parent_id:
                child_count = await self.folder_dao.count_by_parent(db, old_parent_id, folder.project_id)
                await self.folder_dao.update_child_count(db, old_parent_id, child_count)
            
            # 更新新父文件夹的子文件夹数量
            if target_parent_id:
                child_count = await self.folder_dao.count_by_parent(db, target_parent_id, folder.project_id)
                await self.folder_dao.update_child_count(db, target_parent_id, child_count)
            
            await db.commit()
            
            logger.info(f"移动文件夹成功: {folder_id} -> {target_parent_id}")
            return folder
            
        except Exception as e:
            await db.rollback()
            logger.error(f"移动文件夹失败: {str(e)}")
            raise

    async def get_children(
        self, 
        db: AsyncSession, 
        project_id: int, 
        parent_id: Optional[int] = None
    ) -> List[FolderDO]:
        """获取子文件夹列表"""
        return await self.folder_dao.select_children(db, parent_id, project_id)

