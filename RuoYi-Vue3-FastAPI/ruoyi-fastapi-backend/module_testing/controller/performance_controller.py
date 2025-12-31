"""
性能测试(K6)专用控制器
专门处理性能测试的完整流程：需求→脚本生成→执行→报告
"""
import json
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
from module_admin.entity.vo.user_vo import CurrentUserModel
from utils.log_util import logger
from utils.response_util import ResponseUtil
from module_testing.entity.vo.script_vo import ExecuteScriptModel, GenerateScriptModel
from module_testing.service.performance_service import PerformanceService


performance_controller = APIRouterPro(
    prefix='/testing/performance',
    order_num=30,
    tags=['性能测试管理-K6'],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@performance_controller.post(
    '/generate-script',
    summary='AI生成K6性能测试脚本',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:performance:generate')]
)
@Log(title='生成K6脚本', business_type=BusinessType.INSERT)
async def generate_k6_script(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    generate_model: Annotated[GenerateScriptModel, Body()],
) -> Response:
    """
    AI生成K6性能测试脚本
    
    调用testing-agents-service的K6 Agent生成脚本
    """
    try:
        result = await PerformanceService.generate_k6_script(
            db=db,
            user_id=current_user.user.user_id,
            user_name=current_user.user.user_name,
            requirement_id=generate_model.requirement_id,
            config=generate_model.config,
        )
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        logger.error(f'生成K6脚本失败: {e}')
        return ResponseUtil.failure(msg=f'生成失败: {str(e)}')


@performance_controller.post(
    '/execute',
    summary='执行K6性能测试',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:performance:execute')]
)
@Log(title='执行K6测试', business_type=BusinessType.OTHER)
async def execute_k6_test(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
    execute_model: Annotated[ExecuteScriptModel, Body()],
) -> Response:
    """
    执行K6性能测试
    
    提交测试任务到testing-agents-service执行
    """
    try:
        result = await PerformanceService.execute_k6_test(
            db=db,
            user_id=current_user.user.user_id,
            script_id=execute_model.script_id,
            config=execute_model.config,
        )
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        logger.error(f'执行K6测试失败: {e}')
        return ResponseUtil.failure(msg=f'执行失败: {str(e)}')


@performance_controller.get(
    '/execution/{execution_id}/status',
    summary='获取K6执行状态',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:performance:query')]
)
async def get_k6_execution_status(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    execution_id: int = Path(..., description='执行ID'),
) -> Response:
    """获取K6执行实时状态"""
    try:
        status = await PerformanceService.get_execution_status(db, execution_id)
        return ResponseUtil.success(dict_content=status)
    except Exception as e:
        logger.error(f'获取执行状态失败: {e}')
        return ResponseUtil.failure(msg=f'获取状态失败: {str(e)}')


@performance_controller.get(
    '/execution/{execution_id}/logs',
    summary='获取K6执行日志(SSE流)',
    dependencies=[UserInterfaceAuthDependency('testing:performance:query')]
)
async def get_k6_execution_logs(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    execution_id: int = Path(..., description='执行ID'),
):
    """
    获取K6执行日志(Server-Sent Events)
    实时推送执行日志到前端
    """
    async def log_stream():
        try:
            async for log_line in PerformanceService.stream_execution_logs(db, execution_id):
                yield f"data: {json.dumps(log_line)}\n\n"
        except Exception as e:
            logger.error(f'日志流推送失败: {e}')
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(log_stream(), media_type='text/event-stream')


@performance_controller.get(
    '/report/{report_id}/download',
    summary='下载K6性能测试报告',
    dependencies=[UserInterfaceAuthDependency('testing:performance:query')]
)
async def download_k6_report(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    report_id: int = Path(..., description='报告ID'),
):
    """下载K6性能测试报告(HTML/JSON)"""
    try:
        file_stream = await PerformanceService.download_report(db, report_id)
        return StreamingResponse(
            file_stream['content'],
            media_type=file_stream['media_type'],
            headers={
                'Content-Disposition': f'attachment; filename="{file_stream["filename"]}"'
            }
        )
    except Exception as e:
        logger.error(f'下载报告失败: {e}')
        return ResponseUtil.failure(msg=f'下载失败: {str(e)}')

