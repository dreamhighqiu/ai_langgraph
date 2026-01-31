from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


RUN_ID_PATTERN = re.compile(r"(\\d{8}_\\d{6}_[0-9a-fA-F]{8})")


def generate_run_id(now: datetime | None = None) -> str:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"{timestamp}_{suffix}"


def extract_run_id(text: str) -> str | None:
    match = RUN_ID_PATTERN.search(text or "")
    return match.group(1) if match else None


def ensure_virtual_dir(virtual_dir: str) -> str:
    if not virtual_dir.startswith("/"):
        virtual_dir = "/" + virtual_dir
    return virtual_dir.rstrip("/")


def join_virtual(base_virtual_dir: str, *parts: str) -> str:
    base_virtual_dir = ensure_virtual_dir(base_virtual_dir)
    clean = [p.strip("/\\") for p in parts if p]
    return base_virtual_dir if not clean else f"{base_virtual_dir}/{'/'.join(clean)}"


def resolve_virtual_path(virtual_path: str, workspace_root: str) -> Path:
    relative_path = virtual_path.lstrip("/")
    return Path(workspace_root).resolve() / relative_path


def to_posix_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


def sanitize_basename(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""
    name = re.sub(r"[^\\w.\\-]+", "_", name, flags=re.UNICODE)
    return name.strip("._-")


def _current_run_state_path(workspace_root: str) -> Path:
    return Path(workspace_root).resolve() / ".ui_agent" / "current_run.json"


def set_current_run_id(workspace_root: str, run_id: str) -> None:
    state_path = _current_run_state_path(workspace_root)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(
        json_dumps({"run_id": run_id, "updated_at": datetime.now().isoformat()}),
        encoding="utf-8",
    )


def get_current_run_id(workspace_root: str) -> str | None:
    state_path = _current_run_state_path(workspace_root)
    if not state_path.exists():
        return None
    try:
        data = json_loads(state_path.read_text(encoding="utf-8"))
        run_id = data.get("run_id")
        return run_id if isinstance(run_id, str) and run_id else None
    except Exception:
        return None


def json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2)


def json_loads(text: str) -> Any:
    import json

    return json.loads(text)


@dataclass(frozen=True)
class RunLayout:
    run_id: str
    run_dir_virtual: str
    run_dir_actual: Path
    report_dir_virtual: str
    report_dir_actual: Path
    artifacts_dir_actual: Path
    result_json_actual: Path


def build_run_layout(reports_dir: str, workspace_root: str, run_id: str) -> RunLayout:
    run_dir_virtual = join_virtual(reports_dir, f"report_{run_id}")
    run_dir_actual = resolve_virtual_path(run_dir_virtual, workspace_root)

    report_dir_virtual = join_virtual(run_dir_virtual, "report")
    report_dir_actual = run_dir_actual / "report"

    artifacts_dir_actual = run_dir_actual / "artifacts"
    result_json_actual = run_dir_actual / f"result_{run_id}.json"

    return RunLayout(
        run_id=run_id,
        run_dir_virtual=run_dir_virtual,
        run_dir_actual=run_dir_actual,
        report_dir_virtual=report_dir_virtual,
        report_dir_actual=report_dir_actual,
        artifacts_dir_actual=artifacts_dir_actual,
        result_json_actual=result_json_actual,
    )
