from __future__ import annotations

import os
from typing import Any, Optional, Tuple

from langchain.chat_models import init_chat_model

from ui_agent.core.config import get_config

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


def resolve_openai_config(
    *,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Tuple[str, Optional[str], Optional[str]]:
    config = get_config()
    openai_cfg = config.get_section("openai")

    resolved_model = (
        model
        or openai_cfg.get("model")
        or os.environ.get("OPENAI_MODEL")
    )
    if not resolved_model:
        raise RuntimeError(
            "LLM model is required. Set openai.model or OPENAI_MODEL."
        )

    resolved_api_key = api_key or openai_cfg.get("api_key") or os.environ.get("OPENAI_API_KEY")
    resolved_base_url = base_url or openai_cfg.get("base_url") or os.environ.get("OPENAI_BASE_URL")
    return resolved_model, resolved_api_key, resolved_base_url


def _apply_openai_env(api_key: Optional[str], base_url: Optional[str], require_api_key: bool) -> None:
    if api_key:
        os.environ.setdefault("OPENAI_API_KEY", api_key)
    elif require_api_key and not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OpenAI API key is required for this request.")

    if base_url:
        os.environ.setdefault("OPENAI_BASE_URL", base_url)
        os.environ.setdefault("OPENAI_API_BASE", base_url)


def create_chat_model(
    *,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    require_api_key: bool = False,
    **kwargs: Any,
):
    resolved_model, resolved_api_key, resolved_base_url = resolve_openai_config(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    _apply_openai_env(resolved_api_key, resolved_base_url, require_api_key=require_api_key)
    return init_chat_model(resolved_model, **kwargs)


def create_openai_client(
    *,
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> OpenAI:
    if not OPENAI_AVAILABLE:
        raise ImportError("openai is not installed. Run: pip install openai")

    _, resolved_api_key, resolved_base_url = resolve_openai_config(
        api_key=api_key,
        base_url=base_url,
    )
    if not resolved_api_key:
        raise RuntimeError("OpenAI API key is required for this request.")

    client_kwargs = {"api_key": resolved_api_key}
    if resolved_base_url:
        client_kwargs["base_url"] = resolved_base_url
    return OpenAI(**client_kwargs)
