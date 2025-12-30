"""
测试执行控制器
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
from module_testing.entity.vo.execution_vo import (
    CancelExecutionModel,
    ExecutionDetailModel,
    ExecutionModel,
    ExecutionPageQueryModel,
)
from module_testing.service.execution_service import ExecutionService
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil

execution_controller = APIRouterPro(
    prefix='/testing/execution',
    order_num=52,
    tags=['测试管理-执行监控'],
    dependencies=[PreAuthDependency()]
)


@execution_controller.get(
    '/list',
    summary='获取执行记录分页列表',
    response_model=PageResponseModel[ExecutionModel],
    dependencies=[UserInterfaceAuthDependency('testing:execution:list')],
)
async def get_execution_list(
    request: Request,
    query: Annotated[ExecutionPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取执行记录分页列表"""
    result = await ExecutionService.get_execution_list(db, query, is_page=True)
    logger.info('获取执行列表成功')
    return ResponseUtil.success(dict_content=result)


@execution_controller.get(
    '/statistics',
    summary='获取执行统计数据',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:execution:list')],
)
async def get_execution_statistics(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    days: int = Query(7, description='统计天数'),
) -> Response:
    """获取执行统计数据"""
    result = await ExecutionService.get_statistics(db, days)
    return ResponseUtil.success(data=result)


@execution_controller.get(
    '/running',
    summary='获取正在运行的执行',
    response_model=DataResponseModel[list],
    dependencies=[UserInterfaceAuthDependency('testing:execution:list')],
)
async def get_running_executions(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取正在运行的执行"""
    result = await ExecutionService.get_running_executions(db)
    return ResponseUtil.success(data=result)


@execution_controller.get(
    '/{execution_id}',
    summary='获取执行详情',
    response_model=DataResponseModel[ExecutionDetailModel],
    dependencies=[UserInterfaceAuthDependency('testing:execution:query')],
)
async def get_execution_detail(
    request: Request,
    execution_id: Annotated[int, Path(description='执行ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取执行详情"""
    result = await ExecutionService.get_execution_detail(db, execution_id)
    if result:
        return ResponseUtil.success(data=result)
    return ResponseUtil.error(msg='执行记录不存在')


@execution_controller.get(
    '/{execution_id}/status',
    summary='获取执行状态',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:execution:query')],
)
async def get_execution_status(
    request: Request,
    execution_id: Annotated[int, Path(description='执行ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取执行状态"""
    result = await ExecutionService.get_execution_status(db, execution_id)
    if result:
        return ResponseUtil.success(data=result)
    return ResponseUtil.error(msg='执行记录不存在')


@execution_controller.post(
    '/cancel',
    summary='取消执行',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:execution:cancel')],
)
@Log(title='取消执行', business_type=BusinessType.OTHER)
async def cancel_execution(
    request: Request,
    model: Annotated[CancelExecutionModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """取消执行"""
    result = await ExecutionService.cancel_execution(db, model)
    if result['success']:
        logger.info(f'取消执行: {model.execution_id}')
        return ResponseUtil.success(msg='取消成功')
    return ResponseUtil.error(msg=result.get('error', '取消失败'))


@execution_controller.post(
    '/{execution_id}/retry',
    summary='重试执行',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:execution:query')],
)
@Log(title='重试执行', business_type=BusinessType.OTHER)
async def retry_execution(
    request: Request,
    execution_id: Annotated[int, Path(description='执行ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """重试执行"""
    result = await ExecutionService.retry_execution(db, execution_id, current_user.user.user_name)
    if result['success']:
        logger.info(f'重试执行: {execution_id} -> {result["execution_id"]}')
        return ResponseUtil.success(msg='重试已启动', data=result)
    return ResponseUtil.error(msg=result.get('error', '重试失败'))

