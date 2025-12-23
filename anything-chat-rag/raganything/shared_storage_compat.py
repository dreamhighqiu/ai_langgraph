"""
LightRAG 共享存储接口兼容层。

不同版本的 LightRAG 对 `pipeline_status` 相关的锁/数据访问 API 命名不一致。
MCP/RAGAnything 这侧依旧引用旧函数名，这个模块负责检测当前
LightRAG 的实现并提供统一入口，避免运行时 ImportError。
"""

from __future__ import annotations

from typing import Any, Iterable

from lightrag.kg import shared_storage as _shared_storage  # type: ignore

# 所有版本都存在的函数
get_namespace_data = _shared_storage.get_namespace_data
_get_namespace_lock = getattr(_shared_storage, "get_namespace_lock", None)

if _get_namespace_lock is None:  # pragma: no cover - 理论上不会出现
    raise ImportError(
        "lightrag.kg.shared_storage 缺少 get_namespace_lock，无法构建兼容层"
    )


if hasattr(_shared_storage, "get_pipeline_status_lock"):
    get_pipeline_status_lock = _shared_storage.get_pipeline_status_lock
else:

    def get_pipeline_status_lock(
        enable_logging: bool = False, workspace: str | None = None
    ):
        return _get_namespace_lock("pipeline_status", workspace, enable_logging)


if hasattr(_shared_storage, "get_pipeline_status_history"):
    get_pipeline_status_history = _shared_storage.get_pipeline_status_history
else:

    async def get_pipeline_status_history(
        workspace: str | None = None,
    ) -> Iterable[Any] | list[Any]:
        pipeline_status = await get_namespace_data(
            "pipeline_status", workspace=workspace
        )
        history = pipeline_status.get("history_messages")
        if history is None:
            history = []
            pipeline_status["history_messages"] = history
        return history


if hasattr(_shared_storage, "get_pipeline_status_history_lock"):
    get_pipeline_status_history_lock = (
        _shared_storage.get_pipeline_status_history_lock
    )
else:

    def get_pipeline_status_history_lock(
        enable_logging: bool = False, workspace: str | None = None
    ):
        return _get_namespace_lock("pipeline_status", workspace, enable_logging)


__all__ = [
    "get_namespace_data",
    "get_pipeline_status_lock",
    "get_pipeline_status_history",
    "get_pipeline_status_history_lock",
]
