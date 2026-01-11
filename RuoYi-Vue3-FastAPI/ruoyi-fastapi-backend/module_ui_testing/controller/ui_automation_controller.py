"""
UI自动化测试控制器
提供UI自动化测试相关的API接口
"""

from typing import Annotated

from fastapi import Body, Depends, Path, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from common.annotation.log_annotation import Log
from common.aspect.db_seesion import DBSessionDependency
from common.aspect.interface_auth import UserInterfaceAuthDependency
from common.aspect.pre_auth import CurrentUserDependency, PreAuthDependency
from common.enums import BusinessType
from common.router import APIRouterPro
from common.vo import DataResponseModel, PageResponseModel, ResponseBaseModel
from module_admin.entity.vo.user_vo import CurrentUserModel
from module_ui_testing.entity.vo.ui_script_vo import UIScriptModel, UIScriptPageQueryModel
from module_ui_testing.service.ui_script_service import UIScriptService
from module_ui_testing.entity.vo.ui_script_vo import (
    UIExecutionResponse,
    UIReportResponse,
    UIScriptExecuteRequest,
    UIScriptGenerateRequest,
    UIScriptResponse,
)
from module_testing.entity.vo.execution_vo import ExecutionPageQueryModel
from module_testing.entity.vo.report_vo import ReportPageQueryModel
from module_ui_testing.service.ui_automation_service import UIAutomationService
from utils.log_util import logger
from utils.response_util import ResponseUtil

ui_automation_controller = APIRouterPro(
    prefix="/api/testing/ui-automation",
    order_num=52,
    tags=["测试管理-UI自动化"],
    dependencies=[PreAuthDependency()],
    auto_register=True,
)


@ui_automation_controller.post(
    "/generate",
    summary="AI生成UI自动化测试脚本",
    response_model=DataResponseModel[UIScriptResponse],
    dependencies=[UserInterfaceAuthDependency("testing:script:generate")],
)
@Log(title="AI生成UI自动化脚本", business_type=BusinessType.INSERT)
async def generate_ui_script(
    request: Request,
    model: Annotated[UIScriptGenerateRequest, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    AI生成UI自动化测试脚本

    根据测试需求描述使用AI智能生成Playwright测试脚本。
    支持TypeScript和JavaScript两种语言。
    """
    try:
        result = await UIAutomationService.generate_script(
            db=db, request=model, creator=current_user.user.user_name
        )

        if result["success"]:
            logger.info(f"AI生成UI自动化脚本成功: {result['script_id']}")
            return ResponseUtil.success(msg="生成成功", data=result)
        else:
            logger.error(f"AI生成UI自动化脚本失败: {result.get('error')}")
            return ResponseUtil.error(msg=result.get("error", "生成失败"))

    except Exception as e:
        logger.error(f"AI生成UI自动化脚本异常: {str(e)}")
        return ResponseUtil.error(msg=f"生成失败: {str(e)}")


@ui_automation_controller.get(
    "/scripts",
    summary="获取UI自动化脚本列表",
    response_model=PageResponseModel[UIScriptModel],
    dependencies=[UserInterfaceAuthDependency("testing:script:list")],
)
async def get_ui_script_list(
    request: Request,
    query: Annotated[UIScriptPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化脚本列表（Playwright类型）"""
    result = await UIScriptService.get_script_list(db, query, is_page=True)
    logger.info("获取UI自动化脚本列表成功")
    return ResponseUtil.success(dict_content=result)


@ui_automation_controller.get(
    "/scripts/{script_id}",
    summary="获取UI自动化脚本详情",
    response_model=DataResponseModel[UIScriptModel],
    dependencies=[UserInterfaceAuthDependency("testing:script:query")],
)
async def get_ui_script_detail(
    request: Request,
    script_id: Annotated[int, Path(description="脚本ID")],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化脚本详情"""
    script = await UIScriptService.get_script_by_id(db, script_id)
    if script and script.script_type == "playwright":
        return ResponseUtil.success(data=script)
    return ResponseUtil.error(msg="脚本不存在或不是UI自动化脚本")


@ui_automation_controller.post(
    "/execute",
    summary="执行UI自动化测试脚本",
    response_model=DataResponseModel[UIExecutionResponse],
    dependencies=[UserInterfaceAuthDependency("testing:script:execute")],
)
@Log(title="执行UI自动化脚本", business_type=BusinessType.OTHER)
async def execute_ui_script(
    request: Request,
    model: Annotated[UIScriptExecuteRequest, Body()],
    db: Annotated[AsyncSession, DBSessionDependency()],
    current_user: Annotated[CurrentUserModel, CurrentUserDependency()],
) -> Response:
    """
    执行UI自动化测试脚本

    使用Playwright执行测试脚本，生成测试报告。
    """
    try:
        result = await UIAutomationService.execute_script(
            db=db, request=model, executor=current_user.user.user_name
        )

        if result["success"]:
            logger.info(
                f"执行UI自动化脚本: {model.script_id}, execution_id: {result['execution_id']}"
            )
            return ResponseUtil.success(msg="执行已启动", data=result)
        else:
            return ResponseUtil.error(msg=result.get("error", "执行失败"))

    except Exception as e:
        logger.error(f"执行UI自动化脚本异常: {str(e)}")
        return ResponseUtil.error(msg=f"执行失败: {str(e)}")


@ui_automation_controller.get(
    "/executions",
    summary="获取UI自动化执行列表",
    response_model=PageResponseModel[UIExecutionResponse],
    dependencies=[UserInterfaceAuthDependency("testing:execution:list")],
)
async def get_ui_execution_list(
    request: Request,
    query: Annotated[ExecutionPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化执行列表"""
    try:
        from module_testing.dao.execution_dao import ExecutionDAO
        
        # 只查询 playwright 类型的执行
        query.script_type = "playwright"
        executions, total = await ExecutionDAO.get_list(db, query, is_page=True)
        
        # 转换为响应格式
        result = {
            "rows": executions,
            "total": total
        }
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        logger.error(f"获取执行列表失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取失败: {str(e)}")


@ui_automation_controller.get(
    "/executions/{execution_id}",
    summary="获取UI自动化执行详情",
    response_model=DataResponseModel[UIExecutionResponse],
    dependencies=[UserInterfaceAuthDependency("testing:execution:query")],
)
async def get_ui_execution_detail(
    request: Request,
    execution_id: Annotated[int, Path(description="执行ID")],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化执行详情"""
    try:
        result = await UIAutomationService.get_execution_detail(db, execution_id)
        if result:
            return ResponseUtil.success(data=result)
        return ResponseUtil.error(msg="执行记录不存在")
    except Exception as e:
        logger.error(f"获取执行详情失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取失败: {str(e)}")


@ui_automation_controller.get(
    "/executions/{execution_id}/reports",
    summary="获取UI自动化测试报告列表（按执行ID）",
    response_model=DataResponseModel[list[UIReportResponse]],
    dependencies=[UserInterfaceAuthDependency("testing:report:list")],
)
async def get_ui_execution_reports(
    request: Request,
    execution_id: Annotated[int, Path(description="执行ID")],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化测试报告列表（按执行ID）"""
    try:
        result = await UIAutomationService.get_execution_reports(db, execution_id)
        return ResponseUtil.success(data=result)
    except Exception as e:
        logger.error(f"获取测试报告列表失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取失败: {str(e)}")


@ui_automation_controller.get(
    "/reports",
    summary="获取UI自动化测试报告列表",
    response_model=PageResponseModel[UIReportResponse],
    dependencies=[UserInterfaceAuthDependency("testing:report:list")],
)
async def get_ui_report_list(
    request: Request,
    query: Annotated[ReportPageQueryModel, Query()],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """获取UI自动化测试报告列表"""
    try:
        from module_testing.dao.report_dao import ReportDAO
        
        # 只查询 playwright 类型的报告
        query.report_type = "playwright"
        reports, total = await ReportDAO.get_list(db, query, is_page=True)
        
        # 转换为响应格式
        result = {
            "rows": reports,
            "total": total
        }
        return ResponseUtil.success(dict_content=result)
    except Exception as e:
        logger.error(f"获取报告列表失败: {str(e)}")
        return ResponseUtil.error(msg=f"获取失败: {str(e)}")


@ui_automation_controller.get(
    "/reports/{report_id}/download",
    summary="下载UI自动化测试报告",
    dependencies=[UserInterfaceAuthDependency("testing:report:download")],
)
async def download_ui_report(
    request: Request,
    report_id: Annotated[int, Path(description="报告ID")],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """下载UI自动化测试报告"""
    try:
        result = await UIAutomationService.download_report(db, report_id)
        if result["success"]:
            # 返回文件下载响应
            from fastapi.responses import StreamingResponse
            import io

            return StreamingResponse(
                io.BytesIO(result["content"]),
                media_type=result["content_type"],
                headers={
                    "Content-Disposition": f'attachment; filename="{result["filename"]}"'
                },
            )
        return ResponseUtil.error(msg=result.get("error", "下载失败"))
    except Exception as e:
        logger.error(f"下载测试报告失败: {str(e)}")
        return ResponseUtil.error(msg=f"下载失败: {str(e)}")


@ui_automation_controller.delete(
    "/scripts/{script_id}",
    summary="删除UI自动化脚本",
    response_model=ResponseBaseModel,
    dependencies=[UserInterfaceAuthDependency("testing:script:remove")],
)
@Log(title="删除UI自动化脚本", business_type=BusinessType.DELETE)
async def delete_ui_script(
    request: Request,
    script_id: Annotated[int, Path(description="脚本ID")],
    db: Annotated[AsyncSession, DBSessionDependency()],
) -> Response:
    """删除UI自动化脚本"""
    try:
        # 使用UIScriptService的删除方法
        from module_ui_testing.entity.vo.ui_script_vo import DeleteUIScriptModel

        model = DeleteUIScriptModel(script_ids=[script_id])
        result = await UIScriptService.delete_scripts(db, model)

        if result["success"]:
            return ResponseUtil.success(msg="删除成功")
        return ResponseUtil.error(msg=result.get("error", "删除失败"))
    except Exception as e:
        logger.error(f"删除UI自动化脚本失败: {str(e)}")
        return ResponseUtil.error(msg=f"删除失败: {str(e)}")

