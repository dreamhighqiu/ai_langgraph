import base64
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ui_agent.automation.runtime_config import get_runtime_config
from ui_agent.automation.run_storage import build_run_layout, get_current_run_id


BASE64_PATTERN = re.compile(r'\\?"base64Data\\?"\\s*:\\s*\\?"([A-Za-z0-9+/=]{50,}.*?)\\?"')


def _save_base64_image(base64_data: str, message_id: str) -> str:
    cfg = get_runtime_config()
    images_dir = Path(cfg.workspace_root) / cfg.base64_images_dir.lstrip("/")
    run_id = get_current_run_id(cfg.workspace_root)
    if run_id:
        images_dir = build_run_layout(cfg.reports_dir, cfg.workspace_root, run_id).run_dir_actual / "images"
    images_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"{message_id}_{timestamp}.png"
    filepath = images_dir / filename

    try:
        image_bytes = base64.b64decode(base64_data)
        filepath.write_bytes(image_bytes)
        return str(filepath.absolute())
    except Exception as exc:
        return f"[ERROR: Failed to save image - {exc}]"


def contains_base64(content: Any) -> bool:
    if content is None:
        return False

    if isinstance(content, str):
        return bool(BASE64_PATTERN.search(content))

    if isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                text = item.get("text", "")
                if isinstance(text, str) and BASE64_PATTERN.search(text):
                    return True
            elif isinstance(item, str) and BASE64_PATTERN.search(item):
                return True

    return False


def replace_base64_in_content(content: Any, message_id: str) -> Any:
    def replace_match(match: re.Match) -> str:
        base64_data = match.group(1)
        saved_path = _save_base64_image(base64_data, message_id)
        return f'"base64Data": "[BASE64_IMAGE_SAVED: {saved_path}]"'

    if isinstance(content, str):
        return BASE64_PATTERN.sub(replace_match, content)

    if isinstance(content, list):
        new_content = []
        for item in content:
            if isinstance(item, dict) and "text" in item:
                new_item = item.copy()
                if isinstance(item["text"], str):
                    new_item["text"] = BASE64_PATTERN.sub(replace_match, item["text"])
                new_content.append(new_item)
            else:
                new_content.append(item)
        return new_content

    return content
