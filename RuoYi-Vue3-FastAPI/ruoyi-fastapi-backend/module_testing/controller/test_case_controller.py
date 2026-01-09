"""
测试用例控制器
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.service.test_case_service import TestCaseService
from module_testing.entity.vo.test_case_vo import (
    TestCaseCreateVO, TestCaseUpdateVO, TestCaseQueryVO, TestCaseAIGenerateVO
)
from config.get_db import get_db
from module_admin.service.login_service import LoginService
from common.annotation.log_annotation import Log
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.enums import BusinessType
from utils.response_util import ResponseUtil
from utils.log_util import logger


router = APIRouter(prefix="/testing/test-case", tags=["测试用例管理"])
test_case_service = TestCaseService()


@router.post("", summary="创建测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='测试用例管理', business_type=BusinessType.INSERT)
async def create_test_case(
    test_case_vo: TestCaseCreateVO,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """创建测试用例"""
    try:
        result = await test_case_service.create_test_case(
            db, test_case_vo, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(data={
            'case_id': result.case_id,
            'case_identifier': result.case_identifier
        }, msg="创建测试用例成功")
        
    except Exception as e:
        logger.error(f"创建测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"创建测试用例失败: {str(e)}")


@router.put("/{case_id}", summary="更新测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:edit')])
@Log(title='测试用例管理', business_type=BusinessType.UPDATE)
async def update_test_case(
    test_case_vo: TestCaseUpdateVO,
    case_id: int = Path(..., description="测试用例ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """更新测试用例"""
    try:
        result = await test_case_service.update_test_case(
            db, case_id, test_case_vo, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(data={
            'case_id': result.case_id
        }, msg="更新测试用例成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"更新测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"更新测试用例失败: {str(e)}")


@router.get("/list", summary="查询测试用例列表", dependencies=[UserInterfaceAuthDependency('testing:testcase:list')])
async def query_test_case_list(
    project_id: Optional[int] = Query(None, description="项目ID"),
    folder_id: Optional[int] = Query(None, description="文件夹ID"),
    case_name: Optional[str] = Query(None, description="用例名称"),
    case_type: Optional[str] = Query(None, description="用例类型"),
    template: Optional[str] = Query(None, description="模板类型"),
    status: Optional[str] = Query(None, description="状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    tags: Optional[str] = Query(None, description="标签"),
    page_num: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """查询测试用例列表"""
    try:
        query_vo = TestCaseQueryVO(
            project_id=project_id,
            folder_id=folder_id,
            case_name=case_name,
            case_type=case_type,
            status=status,
            priority=priority,
            tags=tags,
            page_num=page_num,
            page_size=page_size
        )
        
        records, total = await test_case_service.query_test_case_list(db, query_vo)
        
        return ResponseUtil.success(data={
            'rows': [record.to_dict() for record in records],
            'total': total,
            'page_num': page_num,
            'page_size': page_size
        })
        
    except Exception as e:
        logger.error(f"查询测试用例列表失败: {str(e)}")
        return ResponseUtil.failure(msg=f"查询测试用例列表失败: {str(e)}")


@router.get("/{case_id}", summary="获取测试用例详情", dependencies=[UserInterfaceAuthDependency('testing:testcase:query')])
async def get_test_case(
    case_id: int = Path(..., description="测试用例ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """获取测试用例详情"""
    try:
        result = await test_case_service.get_test_case(db, case_id)
        if result:
            return ResponseUtil.success(data=result.to_dict())
        else:
            return ResponseUtil.failure(msg="测试用例不存在")
    except Exception as e:
        logger.error(f"获取测试用例详情失败: {str(e)}")
        return ResponseUtil.failure(msg=f"获取测试用例详情失败: {str(e)}")


@router.delete("/{case_ids}", summary="删除测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:remove')])
@Log(title='测试用例管理', business_type=BusinessType.DELETE)
async def delete_test_case(
    case_ids: str = Path(..., description="测试用例ID，多个用逗号分隔"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """删除测试用例（支持批量）"""
    try:
        id_list = [int(id.strip()) for id in case_ids.split(',') if id.strip()]
        deleted_count = 0
        for case_id in id_list:
            if await test_case_service.delete_test_case(db, case_id):
                deleted_count += 1
        
        return ResponseUtil.success(msg=f"成功删除 {deleted_count} 个测试用例")
        
    except Exception as e:
        logger.error(f"删除测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"删除测试用例失败: {str(e)}")


@router.post("/batch", summary="批量创建测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='测试用例管理', business_type=BusinessType.INSERT)
async def batch_create_test_cases(
    test_cases: List[TestCaseCreateVO] = Body(..., description="测试用例列表"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """批量创建测试用例"""
    try:
        results = await test_case_service.batch_create_test_cases(
            db, test_cases, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(data={
            'created_count': len(results),
            'case_ids': [r.case_id for r in results]
        }, msg=f"成功创建 {len(results)} 个测试用例")
        
    except Exception as e:
        logger.error(f"批量创建测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"批量创建测试用例失败: {str(e)}")


@router.put("/move/{case_id}", summary="移动测试用例到文件夹", dependencies=[UserInterfaceAuthDependency('testing:testcase:edit')])
@Log(title='测试用例管理', business_type=BusinessType.UPDATE)
async def move_test_case(
    case_id: int = Path(..., description="测试用例ID"),
    folder_id: Optional[int] = Body(None, embed=True, description="目标文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """移动测试用例到指定文件夹"""
    try:
        result = await test_case_service.move_test_case(
            db, case_id, folder_id, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(data={
            'case_id': result.case_id,
            'folder_id': result.folder_id
        }, msg="移动测试用例成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"移动测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"移动测试用例失败: {str(e)}")


@router.post("/copy/{case_id}", summary="复制测试用例", dependencies=[UserInterfaceAuthDependency('testing:testcase:add')])
@Log(title='测试用例管理', business_type=BusinessType.INSERT)
async def copy_test_case(
    case_id: int = Path(..., description="测试用例ID"),
    folder_id: Optional[int] = Body(None, embed=True, description="目标文件夹ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """复制测试用例"""
    try:
        result = await test_case_service.copy_test_case(
            db, case_id, folder_id, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(data={
            'case_id': result.case_id,
            'case_identifier': result.case_identifier
        }, msg="复制测试用例成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"复制测试用例失败: {str(e)}")
        return ResponseUtil.failure(msg=f"复制测试用例失败: {str(e)}")


@router.put("/status/{case_id}", summary="修改测试用例状态", dependencies=[UserInterfaceAuthDependency('testing:testcase:edit')])
@Log(title='测试用例管理', business_type=BusinessType.UPDATE)
async def change_status(
    case_id: int = Path(..., description="测试用例ID"),
    status: str = Body(..., embed=True, description="状态"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """修改测试用例状态"""
    try:
        result = await test_case_service.change_status(
            db, case_id, status, current_user.get('user_name', 'system')
        )
        
        return ResponseUtil.success(msg="修改状态成功")
        
    except ValueError as e:
        return ResponseUtil.failure(msg=str(e))
    except Exception as e:
        logger.error(f"修改状态失败: {str(e)}")
        return ResponseUtil.failure(msg=f"修改状态失败: {str(e)}")


@router.get("/count/{project_id}", summary="统计项目测试用例数量", dependencies=[UserInterfaceAuthDependency('testing:testcase:list')])
async def count_by_project(
    project_id: int = Path(..., description="项目ID"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(LoginService.get_current_user)
):
    """统计项目下的测试用例数量"""
    try:
        stats = await test_case_service.get_project_stats(db, project_id)
        return ResponseUtil.success(data=stats)
    except Exception as e:
        logger.error(f"统计失败: {str(e)}")
        return ResponseUtil.failure(msg=f"统计失败: {str(e)}")
