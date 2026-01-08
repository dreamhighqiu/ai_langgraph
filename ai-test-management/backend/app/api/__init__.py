"""
API 路由模块

包含所有 API 端点的路由定义
"""


# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2pWR2FBPT06NDJlY2RkY2U=

from fastapi import APIRouter

from .v2 import projects, folders, test_cases, test_runs, test_results, attachments, configurations, test_plans, documents

# 创建 API v2 路由
api_router = APIRouter(prefix="/api/v2")

# 注册子路由
api_router.include_router(projects.router, tags=["项目管理"])
api_router.include_router(folders.router, tags=["文件夹管理"])
api_router.include_router(test_cases.router, tags=["测试用例管理"])
api_router.include_router(test_cases.exports_router, tags=["导出管理"])
api_router.include_router(test_plans.router, tags=["测试计划管理"])
api_router.include_router(test_runs.router, tags=["测试运行管理"])
api_router.include_router(test_results.router, tags=["测试结果管理"])
api_router.include_router(attachments.test_case_attachments_router, tags=["附件管理"])
api_router.include_router(attachments.test_result_attachments_router, tags=["附件管理"])
api_router.include_router(attachments.attachments_router, tags=["附件管理"])
api_router.include_router(configurations.router, tags=["配置管理"])
api_router.include_router(documents.router, tags=["文档管理"])

__all__ = ["api_router"]
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2V2pWR2FBPT06NDJlY2RkY2U=

