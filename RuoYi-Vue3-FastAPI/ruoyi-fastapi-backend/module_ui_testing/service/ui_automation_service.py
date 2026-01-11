"""
UI自动化测试服务层
处理UI自动化测试相关的业务逻辑
"""

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.dao.script_dao import ScriptDAO
from module_testing.entity.do.script_do import TestScript
from module_testing.service.report_service import ReportService
from module_ui_testing.agents import get_ui_automation_agent
from module_ui_testing.entity.vo.ui_script_vo import (
    UIScriptExecuteRequest,
    UIScriptGenerateRequest,
)
from module_ui_testing.service.integration import try_execute_ui_script
from utils.log_util import logger


class UIAutomationService:
    """UI自动化测试服务"""

    @staticmethod
    async def generate_script(
        db: AsyncSession, request: UIScriptGenerateRequest, creator: str
    ) -> dict[str, Any]:
        """
        AI生成UI自动化测试脚本

        Args:
            db: 数据库会话
            request: 生成请求
            creator: 创建者

        Returns:
            生成结果
        """
        try:
            # 获取UI自动化Agent
            agent = get_ui_automation_agent()

            # 构建提示词
            prompt = f"""请帮我生成Playwright UI自动化测试脚本。

测试需求：
{request.requirement}

生成要求：
- 脚本名称：{request.script_name}
- 脚本语言：{request.language}
- 目标浏览器：{request.browser}
- 项目ID：{request.project_id}
{f'- 描述：{request.description}' if request.description else ''}

请生成完整的Playwright测试脚本，包括：
1. 导入必要的模块
2. 测试用例结构（test.describe 和 test）
3. 页面操作和断言
4. 适当的等待和错误处理
5. 清晰的注释说明

{"请先使用RAG检索相关信息，然后基于检索结果生成脚本。" if request.use_rag else ""}

生成完成后，请使用 save_playwright_script 工具保存脚本。"""

            # 调用Agent生成脚本（收集所有消息）
            script_content = ""
            async for message in agent.generate_script(
                user_input=prompt,
                project_id=request.project_id,
                script_type="playwright",
            ):
                # 提取脚本内容
                if hasattr(message, "content") and message.content:
                    script_content += str(message.content)

            # 从Agent响应中提取脚本内容
            # Agent会返回包含脚本的消息，需要解析
            actual_script_content = UIAutomationService._extract_script_content(
                script_content, request.language
            )

            if not actual_script_content:
                return {
                    "success": False,
                    "error": "未能从Agent响应中提取脚本内容",
                }

            # 保存脚本到数据库
            script_data = {
                "project_id": request.project_id,
                "script_name": request.script_name,
                "script_type": "playwright",
                "script_content": actual_script_content,
                "script_language": request.language,
                "description": request.description or "",
                "create_by": creator,
            }

            script_id = await ScriptDAO.create_script(db, script_data)
            await db.commit()

            logger.info(f"UI自动化脚本生成成功: script_id={script_id}")

            return {
                "success": True,
                "script_id": script_id,
                "script_name": request.script_name,
                "script_content": actual_script_content,
                "language": request.language,
            }

        except Exception as e:
            logger.error(f"生成UI自动化脚本失败: {str(e)}")
            await db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    def _extract_script_content(agent_response: str, language: str) -> str:
        """
        从Agent响应中提取脚本内容

        Args:
            agent_response: Agent响应内容
            language: 脚本语言

        Returns:
            提取的脚本内容
        """
        # 尝试提取代码块
        import re

        # 匹配 ```typescript 或 ```javascript 代码块
        pattern = rf"```{language}\n(.*?)```"
        matches = re.findall(pattern, agent_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # 如果没有找到代码块，尝试提取所有代码块
        pattern = r"```(?:typescript|javascript)?\n(.*?)```"
        matches = re.findall(pattern, agent_response, re.DOTALL)

        if matches:
            return matches[0].strip()

        # 如果还是没有找到，返回整个响应（可能Agent直接返回了代码）
        return agent_response.strip()

    @staticmethod
    async def execute_script(
        db: AsyncSession, request: UIScriptExecuteRequest, executor: str
    ) -> dict[str, Any]:
        """
        执行UI自动化测试脚本

        Args:
            db: 数据库会话
            request: 执行请求
            executor: 执行者

        Returns:
            执行结果
        """
        try:
            # 获取脚本信息
            script = await ScriptDAO.get_script_by_id(db, request.script_id)
            if not script:
                return {"success": False, "error": "脚本不存在"}

            if script.script_type != "playwright":
                return {"success": False, "error": "不是UI自动化脚本"}

            # 创建执行记录
            execution_data = {
                "script_id": request.script_id,
                "execution_status": "pending",
                "executor": executor,
            }

            execution_id = await ExecutionDAO.create_execution(db, execution_data)
            await db.commit()

            # 构建执行配置
            execution_config = {
                "browser": request.browser,
                "headless": request.headless,
                "timeout": request.timeout,
                "env_vars": request.env_vars or {},
            }

            # 使用integration层执行脚本
            result = await try_execute_ui_script(
                db=db,
                execution_id=execution_id,
                script=script,
                execution_config=execution_config,
                executor=executor,
            )

            if result:
                return {
                    "success": result.get("success", False),
                    "execution_id": execution_id,
                    "run_id": result.get("run_id"),
                    "status": result.get("status"),
                }
            else:
                return {"success": False, "error": "执行失败"}

        except Exception as e:
            logger.error(f"执行UI自动化脚本失败: {str(e)}")
            await db.rollback()
            return {"success": False, "error": str(e)}

    @staticmethod
    async def get_execution_detail(
        db: AsyncSession, execution_id: int
    ) -> Optional[dict[str, Any]]:
        """
        获取执行详情

        Args:
            db: 数据库会话
            execution_id: 执行ID

        Returns:
            执行详情
        """
        try:
            execution = await ExecutionDAO.get_execution_by_id(db, execution_id)
            if not execution:
                return None

            return {
                "execution_id": execution.execution_id,
                "script_id": execution.script_id,
                "status": execution.execution_status,
                "run_id": execution.thread_id,
                "browser": (
                    execution.result.get("run", {}).get("browser")
                    if execution.result
                    else None
                ),
                "start_time": (
                    execution.start_time.isoformat() if execution.start_time else None
                ),
                "end_time": (
                    execution.end_time.isoformat() if execution.end_time else None
                ),
                "duration": execution.duration,
            }

        except Exception as e:
            logger.error(f"获取执行详情失败: {str(e)}")
            return None

    @staticmethod
    async def get_execution_reports(
        db: AsyncSession, execution_id: int
    ) -> list[dict[str, Any]]:
        """
        获取执行的测试报告列表

        Args:
            db: 数据库会话
            execution_id: 执行ID

        Returns:
            报告列表
        """
        try:
            reports = await ReportService.get_reports_by_execution(db, execution_id)
            return [
                {
                    "report_id": report.report_id,
                    "execution_id": report.execution_id,
                    "report_type": report.report_type,
                    "summary": report.summary,
                    "metrics": report.metrics,
                    "create_time": (
                        report.create_time.isoformat() if report.create_time else None
                    ),
                }
                for report in reports
            ]

        except Exception as e:
            logger.error(f"获取测试报告列表失败: {str(e)}")
            return []

    @staticmethod
    async def download_report(
        db: AsyncSession, report_id: int
    ) -> dict[str, Any]:
        """
        下载测试报告

        Args:
            db: 数据库会话
            report_id: 报告ID

        Returns:
            报告内容
        """
        try:
            report = await ReportService.get_report_by_id(db, report_id)
            if not report:
                return {"success": False, "error": "报告不存在"}

            # 根据报告类型返回不同的内容
            if report.report_type == "html":
                content_type = "text/html"
                filename = f"report_{report_id}.html"
                content = (
                    report.content.encode("utf-8")
                    if isinstance(report.content, str)
                    else report.content
                )
            elif report.report_type == "allure":
                # Playwright HTML报告zip
                content_type = "application/zip"
                filename = f"playwright_report_{report_id}.zip"
                content = report.content
            else:
                content_type = "application/json"
                filename = f"report_{report_id}.json"
                content = (
                    report.content.encode("utf-8")
                    if isinstance(report.content, str)
                    else report.content
                )

            return {
                "success": True,
                "content": content,
                "content_type": content_type,
                "filename": filename,
            }

        except Exception as e:
            logger.error(f"下载测试报告失败: {str(e)}")
            return {"success": False, "error": str(e)}

