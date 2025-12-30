"""
测试脚本控制器
"""
from typing import Annotated

from fastapi import Body, Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_testing.entity.vo.script_vo import (
    AddScriptModel,
    DeleteScriptModel,
    EditScriptModel,
    ExecuteScriptModel,
    GenerateScriptModel,
    GenerateScriptResponse,
    ScriptModel,
    ScriptPageQueryModel,
)
from module_testing.service.script_service import ScriptService
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil

script_controller = APIRouterPro(
    prefix='/testing/script',
    order_num=51,
    tags=['测试管理-脚本管理'],
    dependencies=[PreAuthDependency()]
)


@script_controller.get(
    '/list',
    summary='获取测试脚本分页列表',
    response_model=PageResponseModel[ScriptModel],
    dependencies=[UserInterfaceAuthDependency('testing:script:list')],
)
async def get_script_list(
    request: Request,
    query: Annotated[ScriptPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取测试脚本分页列表"""
    result = await ScriptService.get_script_list(db, query, is_page=True)
    logger.info('获取脚本列表成功')
    return ResponseUtil.success(dict_content=result)


@script_controller.get(
    '/{script_id}',
    summary='获取脚本详情',
    response_model=DataResponseModel[ScriptModel],
    dependencies=[UserInterfaceAuthDependency('testing:script:query')],
)
async def get_script_detail(
    request: Request,
    script_id: Annotated[int, Path(description='脚本ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取脚本详情"""
    script = await ScriptService.get_script_by_id(db, script_id)
    if script:
        return ResponseUtil.success(data=script)
    return ResponseUtil.error(msg='脚本不存在')


@script_controller.post(
    '',
    summary='新增测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:script:add')],
)
@Log(title='测试脚本', business_type=BusinessType.INSERT)
async def add_script(
    request: Request,
    model: Annotated[AddScriptModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """新增测试脚本"""
    result = await ScriptService.create_script(db, model, current_user.user.user_name)
    if result['success']:
        return ResponseUtil.success(msg='新增成功', data={'script_id': result['script_id']})
    return ResponseUtil.error(msg=result.get('error', '新增失败'))


@script_controller.post(
    '/generate',
    summary='AI生成测试脚本',
    response_model=DataResponseModel[GenerateScriptResponse],
    dependencies=[UserInterfaceAuthDependency('testing:script:generate')],
)
@Log(title='AI生成脚本', business_type=BusinessType.INSERT)
async def generate_script(
    request: Request,
    model: Annotated[GenerateScriptModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """AI生成测试脚本"""
    result = await ScriptService.generate_script(db, model, current_user.user.user_name)
    if result['success']:
        logger.info(f'AI生成脚本成功: {result["script_id"]}')
        return ResponseUtil.success(msg='生成成功', data=result)
    logger.error(f'AI生成脚本失败: {result.get("error")}')
    return ResponseUtil.error(msg=result.get('error', '生成失败'))


@script_controller.put(
    '',
    summary='修改测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:script:edit')],
)
@Log(title='测试脚本', business_type=BusinessType.UPDATE)
async def update_script(
    request: Request,
    model: Annotated[EditScriptModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """修改测试脚本"""
    result = await ScriptService.update_script(db, model, current_user.user.user_name)
    if result['success']:
        return ResponseUtil.success(msg='修改成功')
    return ResponseUtil.error(msg=result.get('error', '修改失败'))


@script_controller.delete(
    '/{script_ids}',
    summary='删除测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:script:remove')],
)
@Log(title='测试脚本', business_type=BusinessType.DELETE)
async def delete_scripts(
    request: Request,
    script_ids: Annotated[str, Path(description='脚本ID列表，逗号分隔')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除测试脚本"""
    model = DeleteScriptModel(script_ids=script_ids)
    result = await ScriptService.delete_scripts(db, model)
    if result['success']:
        return ResponseUtil.success(msg='删除成功')
    return ResponseUtil.error(msg=result.get('error', '删除失败'))


@script_controller.post(
    '/execute',
    summary='执行测试脚本',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:script:execute')],
)
@Log(title='执行脚本', business_type=BusinessType.OTHER)
async def execute_script(
    request: Request,
    model: Annotated[ExecuteScriptModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """执行测试脚本"""
    result = await ScriptService.execute_script(db, model, current_user.user.user_name)
    if result['success']:
        logger.info(f'执行脚本: {model.script_id}, execution_id: {result["execution_id"]}')
        return ResponseUtil.success(msg='执行已启动', data=result)
    return ResponseUtil.error(msg=result.get('error', '执行失败'))
