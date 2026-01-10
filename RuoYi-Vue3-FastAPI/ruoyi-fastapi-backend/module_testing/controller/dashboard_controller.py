"""
质量看板控制器
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.aspect.db_seesion import DBSessionDependency
from common.aspect.pre_auth import PreAuthDependency
from common.router import APIRouterPro
from common.vo import DataResponseModel
from module_testing.service.dashboard_service import DashboardService
from utils.response_util import ResponseUtil

dashboard_controller = APIRouterPro(
    prefix="/api/testing/dashboard",
    order_num=49,
    tags=["测试管理-质量看板"],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@dashboard_controller.get(
    "/summary",
    summary="获取质量看板汇总数据",
    response_model=DataResponseModel,
)
async def get_dashboard_summary(
    request: Request,
    db: Annotated[AsyncSession, DBSessionDependency()],
    days: int = Query(7, ge=1, le=90, description="统计天数（近N天）"),
) -> Response:
    result = await DashboardService.get_summary(db, days=days)
    return ResponseUtil.success(data=result)

