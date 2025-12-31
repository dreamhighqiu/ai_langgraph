"""
测试报告控制器
"""
from typing import Annotated

from fastapi import Body, Path, Query, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_testing.entity.vo.report_vo import (
    CompareReportsModel,
    ReportDetailModel,
    ReportModel,
    ReportPageQueryModel,
)
from module_testing.service.report_service import ReportService
from utils.log_util import logger
from utils.response_util import ResponseUtil

report_controller = APIRouterPro(
    prefix='/testing/report',
    order_num=53,
    tags=['测试管理-报告管理'],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@report_controller.get(
    '/list',
    summary='获取测试报告分页列表',
    response_model=PageResponseModel[ReportModel],
    dependencies=[UserInterfaceAuthDependency('testing:report:list')],
)
async def get_report_list(
    request: Request,
    query: Annotated[ReportPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取测试报告分页列表"""
    result = await ReportService.get_report_list(db, query, is_page=True)
    logger.info('获取报告列表成功')
    return ResponseUtil.success(dict_content=result)


@report_controller.get(
    '/{report_id}',
    summary='获取报告详情',
    response_model=DataResponseModel[ReportDetailModel],
    dependencies=[UserInterfaceAuthDependency('testing:report:query')],
)
async def get_report_detail(
    request: Request,
    report_id: Annotated[int, Path(description='报告ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取报告详情"""
    result = await ReportService.get_report_detail(db, report_id)
    if result:
        return ResponseUtil.success(data=result)
    return ResponseUtil.error(msg='报告不存在')


@report_controller.get(
    '/{report_id}/download',
    summary='下载报告',
    dependencies=[UserInterfaceAuthDependency('testing:report:download')],
)
async def download_report(
    request: Request,
    report_id: Annotated[int, Path(description='报告ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """下载报告"""
    result = await ReportService.get_report_download_url(db, report_id)
    if result['success']:
        logger.info(f'下载报告: {report_id}')
        return RedirectResponse(url=result['url'])
    return ResponseUtil.error(msg=result.get('error', '下载失败'))


@report_controller.post(
    '/compare',
    summary='报告对比',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:report:compare')],
)
async def compare_reports(
    request: Request,
    model: Annotated[CompareReportsModel, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """报告对比"""
    result = await ReportService.compare_reports(db, model)
    if result['success']:
        return ResponseUtil.success(data=result)
    return ResponseUtil.error(msg=result.get('error', '对比失败'))


@report_controller.post(
    '/generate/{execution_id}',
    summary='生成HTML报告',
    response_model=DataResponseModel,
    dependencies=[UserInterfaceAuthDependency('testing:report:add')],
)
@Log(title='生成报告', business_type=BusinessType.INSERT)
async def generate_html_report(
    request: Request,
    execution_id: Annotated[int, Path(description='执行ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """生成HTML报告"""
    result = await ReportService.generate_html_report(db, execution_id)
    if result['success']:
        logger.info(f'生成报告: {result["report_id"]}')
        return ResponseUtil.success(msg='生成成功', data=result)
    return ResponseUtil.error(msg=result.get('error', '生成失败'))


@report_controller.delete(
    '/{report_id}',
    summary='删除报告',
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency('testing:report:remove')],
)
@Log(title='删除报告', business_type=BusinessType.DELETE)
async def delete_report(
    request: Request,
    report_id: Annotated[int, Path(description='报告ID')],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除报告"""
    result = await ReportService.delete_report(db, report_id)
    if result['success']:
        logger.info(f'删除报告: {report_id}')
        return ResponseUtil.success(msg='删除成功')
    return ResponseUtil.error(msg=result.get('error', '删除失败'))

