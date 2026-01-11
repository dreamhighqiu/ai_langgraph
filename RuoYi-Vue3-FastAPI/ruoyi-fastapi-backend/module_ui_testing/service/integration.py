"""
Integration helpers to keep UI automation (Playwright) logic inside module_ui_testing.

module_testing should call these helpers without embedding any Playwright/UI-specific details.
"""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.entity.do.script_do import TestScript
from module_testing.storage.minio_client import get_minio_client
from module_ui_testing.service.playwright_execution_service import PlaywrightExecutionService
from utils.log_util import logger


def get_script_file_ext(script_type: str) -> Optional[str]:
    """
    Return storage filename extension for a script type.

    Only UI automation related overrides are defined here.
    """
    if script_type == "playwright":
        return "spec.ts"
    return None


def get_agent_id_for_script_type(script_type: str) -> Optional[str]:
    """
    Return agent id for a script type.

    Only UI automation related overrides are defined here.
    """
    if script_type == "playwright":
        return "ui_automation_agent"
    return None


def get_requirement_type_for_script_type(script_type: str) -> Optional[str]:
    """
    Return requirement_type used in prompt construction for a script type.

    Only UI automation related overrides are defined here.
    """
    if script_type == "playwright":
        return "ui"
    return None


async def try_execute_ui_script(
    *,
    db: AsyncSession,
    execution_id: int,
    script: TestScript,
    execution_config: Optional[dict] = None,
    executor: str = "",
) -> Optional[dict[str, Any]]:
    """
    If the given script belongs to UI automation, execute it and return the result.
    Otherwise, return None.
    """
    if script.script_type != "playwright":
        return None

    script_content = script.script_content

    # Ensure script content is available (fallback to MinIO if needed)
    if (not script_content) and script.script_file_path:
        try:
            minio_client = get_minio_client()
            success, content = minio_client.download_file(script.script_file_path)
            if success and content:
                try:
                    script_content = content.decode("utf-8")
                except Exception:
                    script_content = content.decode("utf-8", errors="replace")
                script.script_content = script_content
        except Exception as e:
            logger.warning(f"从MinIO读取Playwright脚本失败: {e}")

    if not (script_content or "").strip():
        return {
            "success": False,
            "error": "Playwright脚本内容为空，无法执行",
            "execution_id": execution_id,
        }

    return await PlaywrightExecutionService.execute(
        db=db,
        execution_id=execution_id,
        script=script,
        execution_config=execution_config,
        executor=executor,
    )

