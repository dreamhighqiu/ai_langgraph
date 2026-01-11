"""
Integration helpers to keep UI automation (Playwright) logic inside module_ui_testing.

module_testing should call these helpers without embedding any Playwright/UI-specific details.

这个模块提供了UI自动化测试与module_testing的集成接口，确保：
1. UI自动化相关的代码都在module_ui_testing模块内
2. module_testing通过这些接口调用UI自动化功能
3. 保持模块间的清晰分离
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
    
    Args:
        script_type: 脚本类型
        
    Returns:
        文件扩展名，如果不是UI自动化脚本则返回None
    """
    if script_type == "playwright":
        return "spec.ts"
    return None


def get_agent_id_for_script_type(script_type: str) -> Optional[str]:
    """
    Return agent id for a script type.

    Only UI automation related overrides are defined here.
    
    Args:
        script_type: 脚本类型
        
    Returns:
        Agent ID，如果不是UI自动化脚本则返回None
    """
    if script_type == "playwright":
        return "ui_automation_agent"
    return None


def get_requirement_type_for_script_type(script_type: str) -> Optional[str]:
    """
    Return requirement_type used in prompt construction for a script type.

    Only UI automation related overrides are defined here.
    
    Args:
        script_type: 脚本类型
        
    Returns:
        需求类型，如果不是UI自动化脚本则返回None
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
    
    这是UI自动化脚本执行的统一入口，由module_testing调用。
    
    Args:
        db: 数据库会话
        execution_id: 执行ID
        script: 测试脚本对象
        execution_config: 执行配置（浏览器、无头模式等）
        executor: 执行者
        
    Returns:
        执行结果字典，如果不是UI自动化脚本则返回None
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

