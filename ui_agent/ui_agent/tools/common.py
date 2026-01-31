import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from ui_agent.llm import resolve_openai_config


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_async(coro):
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)

    if not loop.is_running():
        return loop.run_until_complete(coro)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro)
        return future.result()


def read_text(path: Optional[str]) -> Optional[str]:
    if not path:
        return None
    file_path = Path(path)
    if not file_path.exists():
        return None
    return file_path.read_text(encoding="utf-8")


def default_output_dir(name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base = REPO_ROOT / "output"
    return base / f"{name}_{timestamp}"


def extract_html(raw_content: Any) -> str:
    if isinstance(raw_content, dict):
        return raw_content.get("html", "") or ""
    if isinstance(raw_content, str):
        try:
            parsed = json.loads(raw_content)
            if isinstance(parsed, dict):
                return parsed.get("html", "") or ""
        except json.JSONDecodeError:
            return ""
    return ""


def normalize_analysis(analysis: Dict[str, Any]) -> Dict[str, Any]:
    normalized = dict(analysis or {})
    normalized.setdefault("url", normalized.get("url_or_key", ""))
    normalized.setdefault("title", "")
    normalized.setdefault("elements", {})
    normalized.setdefault("forms", [])
    normalized.setdefault("api_requests", [])

    raw_content = normalized.get("raw_content")
    if "html" not in normalized or not normalized.get("html"):
        normalized["html"] = extract_html(raw_content)

    return normalized


def get_openai_config(
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None,
) -> Dict[str, str]:
    resolved_model, resolved_key, resolved_base_url = resolve_openai_config(
        model=model,
        api_key=api_key,
        base_url=base_url,
    )
    if not resolved_key:
        raise RuntimeError("OpenAI API key is required. Set openai.api_key or OPENAI_API_KEY.")

    return {
        "api_key": resolved_key,
        "model": resolved_model,
        "base_url": resolved_base_url,
    }
