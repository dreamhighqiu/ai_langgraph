"""
测试项目控制器
"""
from typing import Annotated

from fastapi import Body, Path, Query, Request, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_testing.entity.vo.project_vo import (
    AddProjectModel,
    DeleteProjectModel,
    EditProjectModel,
    ProjectModel,
    ProjectPageQueryModel,
)
from module_testing.service.project_service import ProjectService
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil

project_controller = APIRouterPro(
    prefix='/testing/project',
    order_num=50,
    tags=['测试管理-项目管理'],
    dependencies=[PreAuthDependency()]
)


@project_controller.get(
    '/list',
    summary='获取测试项目分页列表',
    response_model=PageResponseModel[ProjectModel],
    dependencies=[UserInterfaceAuthDependency('testing:project:list')],
)
async def get_project_list(
    request: Request,
    query: Annotated[ProjectPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取测试项目分页列表"""
    result = await ProjectService.get_project_list(db, query, is_page=True)
    logger.info('获取项目列表成功')
    # 返回分页字段需要 dict_content，而非 model_content（model_content 要求 BaseModel）
    return ResponseUtil.success(dict_content=result)


@project_controller.get(
    '/all',
    summary='获取所有测试项目',
    response_model=DataResponseModel[list[ProjectModel]],
    dependencies=[UserInterfaceAuthDependency('testing:project:list')],
)
async def get_all_projects(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    status: str = Query(None, description='状态过滤'),
) -> Response:
    """获取所有项目(下拉选择用)"""
    projects = await ProjectService.get_all_projects(db, status)
    return ResponseUtil.success(data=projects)


@project_controller.get(
    '/{project_id}',
    summary='获取项目详情',
    response_model=DataResponseModel[ProjectModel],
    dependencies=[UserInterfaceAuthDependency('testing:project:query')],
)
async def get_project_detail(
    request: Request,
    project_id: Annotated[int, Path(description='项目ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取项目详情"""
    project = await ProjectService.get_project_by_id(db, project_id)
    if project:
        return ResponseUtil.success(data=project)
    return ResponseUtil.error(msg='项目不存在')


@project_controller.post(
    '',
    summary='新增测试项目',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:project:add')],
)
@Log(title='测试项目', business_type=BusinessType.INSERT)
async def add_project(
    request: Request,
    model: Annotated[AddProjectModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增测试项目"""
    result = await ProjectService.create_project(db, model, current_user.user.user_name)
    if result['success']:
        return ResponseUtil.success(msg='新增成功')
    return ResponseUtil.error(msg=result.get('error', '新增失败'))


@project_controller.put(
    '',
    summary='修改测试项目',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:project:edit')],
)
@Log(title='测试项目', business_type=BusinessType.UPDATE)
async def update_project(
    request: Request,
    model: Annotated[EditProjectModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """修改测试项目"""
    result = await ProjectService.update_project(db, model, current_user.user.user_name)
    if result['success']:
        return ResponseUtil.success(msg='修改成功')
    return ResponseUtil.error(msg=result.get('error', '修改失败'))


@project_controller.delete(
    '/{project_ids}',
    summary='删除测试项目',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:project:remove')],
)
@Log(title='测试项目', business_type=BusinessType.DELETE)
async def delete_projects(
    request: Request,
    project_ids: Annotated[str, Path(description='项目ID列表，逗号分隔')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除测试项目"""
    model = DeleteProjectModel(project_ids=project_ids)
    result = await ProjectService.delete_projects(db, model)
    if result['success']:
        return ResponseUtil.success(msg='删除成功')
    return ResponseUtil.error(msg=result.get('error', '删除失败'))


@project_controller.put(
    '/changeStatus',
    summary='修改项目状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:project:edit')],
)
@Log(title='测试项目', business_type=BusinessType.UPDATE)
async def change_project_status(
    request: Request,
    project_id: int = Body(..., description='项目ID'),
    status: str = Body(..., description='状态'),
    db: Annotated[AsyncSession, DBSessionDependency()] = None,
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()] = None,
) -> Response:
    """修改项目状态"""
    result = await ProjectService.change_status(db, project_id, status, current_user.user.user_name)
    if result['success']:
        return ResponseUtil.success(msg='修改成功')
    return ResponseUtil.error(msg=result.get('error', '修改失败'))

