"""
K6 执行适配器

将 testing-agents-service 中的 k6_agent 任务管理能力接入平台：
1) 将脚本内容落地到 k6_agent 的 workspace/k6_scripts 目录（虚拟路径映射）
2) 提交异步任务到 K6TaskManager，返回 task_id
3) 后台轮询任务状态，回写执行记录（状态/时长/结果/错误信息等）
"""
import asyncio
import threading
from datetime import datetime
from pathlib import Path
from typing import Tuple

from config.database import AsyncSessionLocal
from module_testing.dao.execution_dao import ExecutionDAO
from utils.log_util import logger

# 引入 k6_agent 组件
import sys

# k6_agent 位于仓库根目录的 testing-agents-service/testing-agents-service
AGENT_ROOT = Path(__file__).resolve().parents[4] / "testing-agents-service" / "testing-agents-service"
AGENT_SRC = AGENT_ROOT / "src"
if AGENT_SRC.exists() and str(AGENT_SRC) not in sys.path:
    sys.path.insert(0, str(AGENT_SRC))

try:
    from k6_agent.config import DEFAULT_CONFIG, K6Config
    from k6_agent.tasks import get_task_manager
except Exception as e:  # pragma: no cover - import safety
    logger.error(f"加载 k6_agent 失败: {e}")
    raise


class K6Runner:
    """包装 k6_agent，负责保存脚本、提交任务、同步结果到执行记录。"""

    def __init__(self, config: K6Config | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.manager = get_task_manager(self.config)

    def _ensure_workspace(self) -> Tuple[Path, Path]:
        """确保工作目录存在，返回 scripts_dir / results_dir 的实际路径。"""
        workspace = Path(self.config.workspace_root).resolve()
        scripts_dir = (workspace / self.config.scripts_dir.lstrip("/")).resolve()
        results_dir = (workspace / self.config.results_dir.lstrip("/")).resolve()
        scripts_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)
        return scripts_dir, results_dir

    def save_script(self, script_name: str, script_content: str) -> Tuple[str, Path]:
        """
        保存脚本到 workspace 并返回 (虚拟路径, 实际路径)
        虚拟路径示例：/k6_scripts/{script_name}.js
        """
        scripts_dir, _ = self._ensure_workspace()
        # 默认 js 后缀
        filename = script_name if script_name.endswith(".js") else f"{script_name}.js"
        actual_path = scripts_dir / filename
        actual_path.write_text(script_content, encoding="utf-8")
        virtual_path = f"{self.config.scripts_dir.rstrip('/')}/{filename}"
        return virtual_path, actual_path

    def submit_and_monitor(self, virtual_script_path: str, execution_id: int) -> str:
        """
        提交任务并启动后台线程同步状态到执行记录。
        返回 task_id。
        """
        task_id = self.manager.submit_task(virtual_script_path)
        threading.Thread(
            target=self._monitor_task,
            args=(task_id, execution_id),
            daemon=True,
        ).start()
        return task_id

    def _monitor_task(self, task_id: str, execution_id: int) -> None:
        """后台轮询 k6_task 状态，结束后写入数据库。"""
        async def _sync():
            while True:
                status = self.manager.get_task_status(task_id)
                if not status:
                    logger.warning(f"k6 task 不存在: {task_id}")
                    break
                state = status.get("status")
                # 进行中则等待
                if state in ("pending", "running"):
                    await asyncio.sleep(2)
                    continue

                end_time = None
                start_time = None
                try:
                    if status.get("completed_at"):
                        end_time = datetime.fromisoformat(status["completed_at"])
                    if status.get("started_at"):
                        start_time = datetime.fromisoformat(status["started_at"])
                except Exception:
                    pass

                async with AsyncSessionLocal() as db:
                    if state == "completed":
                        result = status.get("result") or {}
                        await ExecutionDAO.update_result(
                            db,
                            execution_id,
                            result_data=result,
                            status="success",
                            end_time=end_time or datetime.now(),
                        )
                    else:
                        await ExecutionDAO.update_status(
                            db,
                            execution_id,
                            status="failed" if state == "failed" else state,
                            error_msg=status.get("error"),
                            end_time=end_time or datetime.now(),
                        )
                    # 补充开始时间
                    if start_time:
                        await ExecutionDAO.update_status(db, execution_id, status=state, start_time=start_time)
                    await db.commit()
                break

        try:
            asyncio.run(_sync())
        except RuntimeError:
            # 若已存在事件循环，使用新循环
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_sync())
            loop.close()


# 便捷单例
_runner: K6Runner | None = None


def get_k6_runner() -> K6Runner:
    global _runner
    if _runner is None:
        _runner = K6Runner()
    return _runner
