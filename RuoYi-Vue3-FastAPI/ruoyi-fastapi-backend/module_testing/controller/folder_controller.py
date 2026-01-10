"""
文件夹控制器
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query, Path, Request
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.service.folder_service import FolderService
from module_testing.entity.vo.folder_vo import (
    FolderCreateVO, FolderUpdateVO
)
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from common.annotation.log_annotation import Log
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.enums import BusinessType
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/folder", tags=["文件夹管理"])
folder_service = FolderService()


@router.post("", summary="创建文件夹", dependencies=[UserInterfaceAuthDependency('testing:folder:add')])
@Log(title='文件夹管理', business_type=BusinessType.INSERT)
async def create_folder(
    request: Request,
    folder_vo: FolderCreateVO,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(LoginService.get_current_user)
):
    """创建文件夹"""
    try:
        result = await folder_service.create_folder(
            db, folder_vo, current_user.user_name or 'system'
        )
        
        return ResponseUtil.success(data={
            'folder_id': result.folder_id,
            'folder_name': result.folder_name,
            'folder_path': result.folder_path
        }, msg="创建文件夹成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"创建文件夹失败: {str(e)}")
        return ResponseUtil.failure(msg=f"创建文件夹失败: {str(e)}")


@router.put("/{folder_id}", summary="更新文件夹", dependencies=[UserInterfaceAuthDependency('testing:folder:edit')])
@Log(title='文件夹管理', business_type=BusinessType.UPDATE)
async def update_folder(
    request: Request,
    folder_vo: FolderUpdateVO,
    folder_id: int = Path(..., description="文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(LoginService.get_current_user)
):
    """更新文件夹"""
    try:
        result = await folder_service.update_folder(
            db, folder_id, folder_vo, current_user.user_name or 'system'
        )
        
        return ResponseUtil.success(data={
            'folder_id': result.folder_id
        }, msg="更新文件夹成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"更新文件夹失败: {str(e)}")
        return ResponseUtil.failure(msg=f"更新文件夹失败: {str(e)}")


@router.delete("/{folder_id}", summary="删除文件夹", dependencies=[UserInterfaceAuthDependency('testing:folder:remove')])
@Log(title='文件夹管理', business_type=BusinessType.DELETE)
async def delete_folder(
    request: Request,
    folder_id: int = Path(..., description="文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(LoginService.get_current_user)
):
    """删除文件夹"""
    try:
        result = await folder_service.delete_folder(db, folder_id)
        if result:
            return ResponseUtil.success(msg="删除文件夹成功")
        else:
            return ResponseUtil.failure(msg="文件夹不存在")
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"删除文件夹失败: {str(e)}")
        return ResponseUtil.failure(msg=f"删除文件夹失败: {str(e)}")


@router.get("/tree", summary="获取文件夹树", dependencies=[UserInterfaceAuthDependency('testing:folder:list')])
async def get_folder_tree(
    projectId: Optional[int] = Query(None, description="项目ID", ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(LoginService.get_current_user)
):
    """获取文件夹树结构"""
    try:
        # 参数验证
        if not projectId or projectId <= 0:
            return ResponseUtil.failure(msg="项目ID无效，请先选择项目")
        
        tree = await folder_service.get_folder_tree(db, projectId)
        return ResponseUtil.success(data=tree if tree else [])
    except ValueError as e:
        logger.error(f"获取文件夹树失败: {str(e)}")
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"获取文件夹树失败: {str(e)}", exc_info=True)
        return ResponseUtil.failure(msg=f"获取文件夹树失败: {str(e)}")


@router.get("/{folder_id}", summary="获取文件夹详情", dependencies=[UserInterfaceAuthDependency('testing:folder:query')])
async def get_folder(
    folder_id: int = Path(..., description="文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(LoginService.get_current_user)
):
    """获取文件夹详情"""
    try:
        result = await folder_service.get_folder(db, folder_id)
        if result:
            return ResponseUtil.success(data=result.to_dict())
        else:
            return ResponseUtil.failure(msg="文件夹不存在")
    except Exception as e:
        logger.error(f"获取文件夹详情失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取文件夹详情失败: {str(e)}")



