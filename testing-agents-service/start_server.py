#!/usr/bin/env python3
"""
Simple LangGraph API Server

Starts the LangGraph API server directly via uvicorn.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import importlib
import importlib.util
from pathlib import Path
from typing import Optional

# 解决命名冲突：在导入任何其他模块之前，先确保外部 mcp 包被正确导入
# 本地的 mcp 目录会拦截已安装的 mcp 包的导入，导致 ImportError
# 我们需要在导入任何使用 mcp 的模块之前，先强制加载外部包
_local_mcp_dir = Path(__file__).parent / "mcp"
if _local_mcp_dir.exists() and _local_mcp_dir.is_dir():
    # 如果本地 mcp 模块已经在 sys.modules 中，先移除它
    if 'mcp' in sys.modules:
        existing_module = sys.modules['mcp']
        if hasattr(existing_module, '__file__') and existing_module.__file__:
            module_path = Path(existing_module.__file__).resolve()
            if _local_mcp_dir.resolve() in module_path.parents or 'testing-agents-service' in str(module_path):
                # 这是本地模块，需要移除
                del sys.modules['mcp']
                # 同时移除所有 mcp 子模块
                keys_to_remove = [key for key in sys.modules.keys() if key.startswith('mcp.')]
                for key in keys_to_remove:
                    del sys.modules[key]
    
    # 现在强制导入已安装的外部 mcp 包
    try:
        spec = importlib.util.find_spec("mcp")
        if spec and spec.origin and 'site-packages' in spec.origin:
            # 这是已安装的包，强制导入并注册
            external_mcp = importlib.import_module("mcp")
            sys.modules['mcp'] = external_mcp
            # 预加载常用的子模块
            for submodule in ['types', 'client']:
                try:
                    submodule_spec = importlib.util.find_spec(f"mcp.{submodule}")
                    if submodule_spec and submodule_spec.origin and 'site-packages' in submodule_spec.origin:
                        submodule_obj = importlib.import_module(f"mcp.{submodule}")
                        sys.modules[f"mcp.{submodule}"] = submodule_obj
                except Exception:
                    pass
    except Exception:
        # 如果无法导入外部包，继续（可能会在后续导入时失败，但至少不会静默失败）
        pass


def _parse_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "f", "no", "n", "off"}:
        return False
    return default


def _load_graphs() -> dict[str, str]:
    config_path = Path(__file__).parent / "graph.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as file:
        config = json.load(file)
    return config.get("graphs", {}) or {}


def setup_environment(port: int) -> None:
    src_path = Path(__file__).parent / "src"
    sys.path.insert(0, str(src_path))

    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv

            load_dotenv(env_file, override=False)
            print("[OK] Loaded environment from .env")
        except ImportError:
            print("[WARN] python-dotenv not installed, skipping .env file")

    graphs = _load_graphs()

    defaults: dict[str, str] = {
        "DATABASE_URI": ":memory:",
        "REDIS_URI": "fake",
        "MIGRATIONS_PATH": "__inmem",
        "ALLOW_PRIVATE_NETWORK": "true",
        "LANGGRAPH_UI_BUNDLER": "true",
        "LANGGRAPH_RUNTIME_EDITION": "inmem",
        "LANGSMITH_LANGGRAPH_API_VARIANT": "local_dev",
        "LANGGRAPH_DISABLE_FILE_PERSISTENCE": "false",
        "LANGGRAPH_ALLOW_BLOCKING": "true",
        "LANGGRAPH_DEFAULT_RECURSION_LIMIT": "200",
        "LANGSERVE_GRAPHS": json.dumps(graphs) if graphs else "{}",
        "N_JOBS_PER_WORKER": "1",
    }
    for key, value in defaults.items():
        os.environ.setdefault(key, value)

    os.environ["LANGGRAPH_PORT"] = str(port)
    os.environ["LANGGRAPH_API_URL"] = f"http://localhost:{port}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Start LangGraph API server via uvicorn")
    parser.add_argument("--host", default=os.environ.get("LANGGRAPH_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("LANGGRAPH_PORT", "2025")))
    parser.add_argument(
        "--reload",
        default=os.environ.get("LANGGRAPH_RELOAD"),
        help="Enable auto-reload (true/false). Default: true",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reload_enabled = _parse_bool(args.reload, default=True)

    print("Starting Simple LangGraph API Server...")
    setup_environment(args.port)

    print("\n" + "=" * 60)
    print(f"Server URL: http://localhost:{args.port}")
    print(f"API Documentation: http://localhost:{args.port}/docs")
    print(f"Studio UI: http://localhost:{args.port}/ui")
    print(f"Health Check: http://localhost:{args.port}/ok")
    print("=" * 60)

    try:
        import uvicorn

        uvicorn.run(
            "langgraph_api.server:app",
            host=args.host,
            port=args.port,
            reload=reload_enabled,
            access_log=False,
            log_config={
                "version": 1,
                "disable_existing_loggers": False,
                "formatters": {
                    "default": {"format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
                },
                "handlers": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    }
                },
                "root": {"level": "INFO", "handlers": ["default"]},
                "loggers": {
                    "uvicorn": {"level": "INFO"},
                    "uvicorn.error": {"level": "INFO"},
                    "uvicorn.access": {"level": "WARNING"},
                },
            },
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as exc:
        print(f"Server failed to start: {exc}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

