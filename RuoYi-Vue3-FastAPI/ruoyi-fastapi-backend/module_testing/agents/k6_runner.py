"""
本地 K6 运行适配器

目标：隔离 testing-agents-service 的 k6_agent 代码，AI 平台内部独立管理脚本/执行/结果。
功能：
1) 保存脚本到本地 workspace（按项目/需求分目录，便于隔离管理）
2) 提交 K6 任务到后台线程执行
3) 轮询执行结果并写回 ExecutionDAO
"""

import asyncio
import json
import os
import subprocess
import threading
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Tuple

from config.database import AsyncSessionLocal
from module_testing.dao.execution_dao import ExecutionDAO
from utils.log_util import logger


# ------------------------ 基础配置 ------------------------ #
def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int = 0) -> int:
    return int(os.environ.get(key, str(default)))


@dataclass
class K6RunnerConfig:
    """K6 运行配置（本地隔离版）"""

    workspace_root: str = field(default_factory=lambda: _env("K6_WORKSPACE_ROOT", "."))
    scripts_dir: str = field(default_factory=lambda: _env("K6_SCRIPTS_DIR", "/k6_scripts"))
    results_dir: str = field(default_factory=lambda: _env("K6_RESULTS_DIR", "/k6_results"))
    k6_binary: str = field(default_factory=lambda: _env("K6_BINARY", "k6"))
    default_vus: int = field(default_factory=lambda: _env_int("K6_DEFAULT_VUS", 10))
    default_duration: str = field(default_factory=lambda: _env("K6_DEFAULT_DURATION", "1m"))


DEFAULT_CONFIG = K6RunnerConfig()


# ------------------------ 工具函数 ------------------------ #
def _resolve_virtual_path(virtual_path: str, workspace_root: str) -> Path:
    """将虚拟路径（/k6_scripts/xxx）解析为实际路径"""
    relative = virtual_path.lstrip("/")
    return Path(workspace_root).resolve() / relative


def _to_virtual_path(base_dir: str, *parts: str) -> str:
    base = base_dir.strip("/")
    clean_parts = [p.strip("/\\") for p in parts if p]
    return "/" + "/".join([base] + clean_parts)


# ------------------------ 任务模型 ------------------------ #
class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class K6Task:
    task_id: str
    script_path: str  # 虚拟路径
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    started_at: str | None = None
    completed_at: str | None = None
    progress: int = 0
    result: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "script_path": self.script_path,
            "status": self.status.value,
            "created_at": self.created_at,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "progress": self.progress,
            "result": self.result,
            "error": self.error,
        }


class K6TaskManager:
    """本地 K6 任务管理器，负责异步执行与状态维护"""

    def __init__(self, config: K6RunnerConfig | None = None):
        self.config = config or DEFAULT_CONFIG
        self._tasks: dict[str, K6Task] = {}
        self._lock = threading.Lock()
        self._on_complete: Callable[[K6Task], None] | None = None

    def set_on_complete(self, callback: Callable[[K6Task], None]) -> None:
        self._on_complete = callback

    def submit_task(self, script_path: str) -> str:
        task_id = f"k6_{uuid.uuid4().hex[:12]}"
        task = K6Task(task_id=task_id, script_path=script_path, created_at=datetime.now().isoformat())
        with self._lock:
            self._tasks[task_id] = task

        thread = threading.Thread(target=self._execute_task, args=(task_id,), daemon=True)
        thread.start()
        return task_id

    def get_task_status(self, task_id: str) -> dict[str, Any] | None:
        with self._lock:
            task = self._tasks.get(task_id)
            return task.to_dict() if task else None

    def _execute_task(self, task_id: str) -> None:
        with self._lock:
            task = self._tasks.get(task_id)
            if not task or task.status == TaskStatus.CANCELLED:
                return
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now().isoformat()

        try:
            actual_script_path = _resolve_virtual_path(task.script_path, self.config.workspace_root)
            result_filename = f"result_{task_id}.json"
            virtual_result_path = _to_virtual_path(self.config.results_dir, result_filename)
            actual_result_path = _resolve_virtual_path(virtual_result_path, self.config.workspace_root)
            actual_result_path.parent.mkdir(parents=True, exist_ok=True)

            cmd = [
                self.config.k6_binary,
                "run",
                str(actual_script_path),
                "--out",
                f"json={actual_result_path}",
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

            self._update_progress(task_id, process)

            stdout, stderr = process.communicate(timeout=600)

            with self._lock:
                task = self._tasks.get(task_id)
                if not task:
                    return
                task.completed_at = datetime.now().isoformat()
                task.progress = 100

                if process.returncode == 0:
                    task.status = TaskStatus.COMPLETED
                    task.result = {
                        "success": True,
                        "result_file": virtual_result_path,
                        "stdout": stdout,
                    }
                    if actual_result_path.exists():
                        task.result["metrics"] = self._parse_results(actual_result_path)
                else:
                    task.status = TaskStatus.FAILED
                    task.error = stderr
                    task.result = {"success": False, "stderr": stderr}

            if self._on_complete and task:
                self._on_complete(task)

        except subprocess.TimeoutExpired:
            with self._lock:
                task = self._tasks.get(task_id)
                if task:
                    task.status = TaskStatus.FAILED
                    task.error = "执行超时（10分钟）"
                    task.completed_at = datetime.now().isoformat()
        except Exception as exc:  # pragma: no cover - 捕获安全
            with self._lock:
                task = self._tasks.get(task_id)
                if task:
                    task.status = TaskStatus.FAILED
                    task.error = str(exc)
                    task.completed_at = datetime.now().isoformat()

    def _update_progress(self, task_id: str, process: subprocess.Popen) -> None:
        """模拟进度更新"""
        def update():
            progress = 0
            while process.poll() is None and progress < 95:
                time.sleep(2)
                progress = min(progress + 5, 95)
                with self._lock:
                    task = self._tasks.get(task_id)
                    if task:
                        task.progress = progress

        threading.Thread(target=update, daemon=True).start()

    def _parse_results(self, result_file: Path) -> dict[str, Any]:
        """解析 k6 JSON 行输出"""
        metrics: dict[str, Any] = {
            "http_req_duration": {"values": []},
            "http_reqs": {"count": 0},
            "vus": {"max": 0},
            "iterations": {"count": 0},
        }

        try:
            with open(result_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        data = json.loads(line.strip())
                        if data.get("type") != "Point":
                            continue
                        metric = data.get("metric")
                        value = data.get("data", {}).get("value", 0)
                        if metric == "http_req_duration":
                            metrics["http_req_duration"]["values"].append(value)
                        elif metric == "http_reqs":
                            metrics["http_reqs"]["count"] += 1
                        elif metric == "vus":
                            metrics["vus"]["max"] = max(metrics["vus"]["max"], value)
                        elif metric == "iterations":
                            metrics["iterations"]["count"] += 1
                    except json.JSONDecodeError:
                        continue

            durations = metrics["http_req_duration"]["values"]
            if durations:
                durations.sort()
                metrics["http_req_duration"] = {
                    "avg": sum(durations) / len(durations),
                    "min": durations[0],
                    "max": durations[-1],
                    "p90": durations[int(len(durations) * 0.9)],
                    "p95": durations[int(len(durations) * 0.95)],
                    "p99": durations[int(len(durations) * 0.99)],
                }
        except Exception as exc:  # pragma: no cover - 解析容错
            metrics["parse_error"] = str(exc)
        return metrics


# ------------------------ Runner 封装 ------------------------ #
class K6Runner:
    """本地 K6 Runner：保存脚本 -> 提交任务 -> 同步结果到执行记录"""

    def __init__(self, config: K6RunnerConfig | None = None) -> None:
        self.config = config or DEFAULT_CONFIG
        self.manager = K6TaskManager(self.config)

    def _ensure_workspace(self) -> Tuple[Path, Path]:
        workspace = Path(self.config.workspace_root).resolve()
        scripts_dir = (workspace / self.config.scripts_dir.lstrip("/")).resolve()
        results_dir = (workspace / self.config.results_dir.lstrip("/")).resolve()
        scripts_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)
        return scripts_dir, results_dir

    def save_script(
        self,
        script_name: str,
        script_content: str,
        *,
        project_id: int | None = None,
        requirement_id: int | None = None,
    ) -> Tuple[str, Path]:
        """
        保存脚本到 workspace，按项目/需求分目录实现隔离。
        返回: (虚拟路径, 实际路径)
        虚拟路径示例: /k6_scripts/project_1/req_2/login.js
        """
        scripts_dir, _ = self._ensure_workspace()
        filename = script_name if script_name.endswith(".js") else f"{script_name}.js"

        sub_parts: list[str] = []
        if project_id:
            sub_parts.append(f"project_{project_id}")
        if requirement_id:
            sub_parts.append(f"req_{requirement_id}")

        actual_dir = scripts_dir.joinpath(*sub_parts)
        actual_dir.mkdir(parents=True, exist_ok=True)
        actual_path = actual_dir / filename
        actual_path.write_text(script_content, encoding="utf-8")

        virtual_path = _to_virtual_path(self.config.scripts_dir, *sub_parts, filename)
        return virtual_path, actual_path

    def submit_and_monitor(self, virtual_script_path: str, execution_id: int) -> str:
        task_id = self.manager.submit_task(virtual_script_path)
        threading.Thread(
            target=self._monitor_task,
            args=(task_id, execution_id),
            daemon=True,
        ).start()
        return task_id

    def _monitor_task(self, task_id: str, execution_id: int) -> None:
        """后台轮询 k6 任务状态并写回 ExecutionDAO"""

        async def _sync():
            while True:
                status = self.manager.get_task_status(task_id)
                if not status:
                    logger.warning(f"k6 task 不存在: {task_id}")
                    break
                state = status.get("status")
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
                    if start_time:
                        await ExecutionDAO.update_status(db, execution_id, status=state, start_time=start_time)
                    await db.commit()
                break

        try:
            asyncio.run(_sync())
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(_sync())
            loop.close()


_runner: K6Runner | None = None


def get_k6_runner() -> K6Runner:
    global _runner
    if _runner is None:
        _runner = K6Runner()
    return _runner
