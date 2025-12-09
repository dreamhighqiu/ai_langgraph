import asyncio
import importlib
import sys
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable

from ..models import Agent

DEEP_AGENT_SRC = Path(__file__).resolve().parents[2] / "testing-deep-agents-service" / "src"
if DEEP_AGENT_SRC.exists():
    sys.path.append(str(DEEP_AGENT_SRC))


@lru_cache(maxsize=64)
def _load_callable(module_path: str, entrypoint: str) -> Callable[..., Any]:
    module = importlib.import_module(module_path)
    target = getattr(module, entrypoint)
    return target


async def _invoke_callable(callable_obj: Any, payload: Any) -> Any:
    if hasattr(callable_obj, "ainvoke"):
        return await callable_obj.ainvoke(payload)
    if hasattr(callable_obj, "invoke"):
        return callable_obj.invoke(payload)
    if hasattr(callable_obj, "arun"):
        return await callable_obj.arun(payload)
    if hasattr(callable_obj, "run"):
        return callable_obj.run(payload)
    if asyncio.iscoroutinefunction(callable_obj):
        return await callable_obj(payload)
    if callable(callable_obj):
        return callable_obj(payload)
    raise RuntimeError("入口不可调用")


def _build_structured_input(user_input: str) -> dict[str, Any]:
    return {
        "messages": [
            {
                "role": "user",
                "content": user_input,
            }
        ]
    }


async def run_agent(agent: Agent, user_input: str) -> Any:
    callable_obj = _load_callable(agent.graph_module, agent.graph_entrypoint)

    try:
        return await _invoke_callable(callable_obj, user_input)
    except Exception as exc:
        message = str(exc)
        if "Expected dict" in message or "dict" in message:
            structured = _build_structured_input(user_input)
            return await _invoke_callable(callable_obj, structured)
        raise RuntimeError(
            f"Agent {agent.slug} 执行失败: {message}"
        ) from exc
