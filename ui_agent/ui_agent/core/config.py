"""
Configuration loader for ui_agent.
Loads config/config.yaml and config/mcp.yaml by default.
Supports UI_AGENT_CONFIG_DIR override and ${ENV_VAR} expansion.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class Config:
    """Configuration manager (singleton)."""

    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._config is None:
            self._config = self._load_config()

    def _load_dir_config(self, config_dir: Path) -> Dict[str, Any]:
        files = []
        config_file = config_dir / "config.yaml"
        mcp_file = config_dir / "mcp.yaml"
        if config_file.exists():
            files.append(config_file)
        if mcp_file.exists():
            files.append(mcp_file)

        merged: Dict[str, Any] = {}
        for file_path in files:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            merged = self._deep_merge(merged, data)
        return merged

    def _deep_merge(self, base: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        merged = dict(base)
        for key, value in new.items():
            if (
                key in merged
                and isinstance(merged[key], dict)
                and isinstance(value, dict)
            ):
                merged[key] = self._deep_merge(merged[key], value)
            else:
                merged[key] = value
        return merged

    def _load_config(self) -> Dict[str, Any]:
        if not YAML_AVAILABLE:
            return self._get_default_config()

        config_dir_env = os.environ.get("UI_AGENT_CONFIG_DIR")
        if config_dir_env:
            config_dir = Path(config_dir_env)
        else:
            config_dir = Path(__file__).resolve().parents[1] / "config"

        if config_dir.exists():
            try:
                config = self._load_dir_config(config_dir)
                return self._resolve_env_vars(config)
            except Exception as exc:
                print(f"Warning: failed to load config directory: {exc}")

        return self._get_default_config()

    def _resolve_env_vars(self, obj: Any) -> Any:
        """Recursively replace ${VAR_NAME} with environment values."""
        if isinstance(obj, dict):
            return {k: self._resolve_env_vars(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self._resolve_env_vars(item) for item in obj]
        if isinstance(obj, str):
            pattern = r"\$\{([^}]+)\}"
            matches = re.findall(pattern, obj)
            result = obj
            for var_name in matches:
                env_value = os.environ.get(var_name, "")
                result = result.replace(f"${{{var_name}}}", env_value)
            return result
        return obj

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "test_generation": {
                "priority_threshold": "P2",
                "max_cases_per_feature": 20,
                "types": ["functional", "ui", "security", "boundary", "e2e"],
                "automation": {
                    "enabled": True,
                    "framework": "playwright",
                    "language": "java",
                },
            },
            "playwright": {
                "headless": True,
                "timeout": 30000,
                "browser": {"type": "chromium"},
            },
            "figma": {
                "token": os.environ.get("FIGMA_TOKEN", ""),
                "timeout": 10000,
            },
            "output": {
                "directory": "./test_cases",
                "format": ["excel", "xmind"],
            },
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with dot notation."""
        keys = key.split(".")
        value = self._config

        try:
            for part in keys:
                value = value.get(part) if isinstance(value, dict) else default
                if value is None:
                    return default
            return value
        except (KeyError, TypeError):
            return default

    def get_section(self, section: str) -> Dict[str, Any]:
        return self._config.get(section, {})

    @property
    def config(self) -> Dict[str, Any]:
        return self._config

    def reload(self):
        self._config = self._load_config()


_config = None


def get_config() -> Config:
    global _config
    if _config is None:
        _config = Config()
    return _config


def get_figma_token() -> str:
    return os.environ.get("FIGMA_TOKEN", "") or get_config().get("figma.token", "")


def get_playwright_config() -> Dict[str, Any]:
    return get_config().get_section("playwright")


def get_automation_framework() -> str:
    return get_config().get("test_generation.automation.framework", "playwright")


def get_automation_language() -> str:
    return get_config().get("test_generation.automation.language", "python")


def get_output_dir() -> str:
    return get_config().get("output.directory", "./test_cases")
