from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from dotenv import load_dotenv


def _find_webui_dir(repo_root: Path) -> Path:
    candidates = [
        repo_root / "sum_mcp_server" / "vendor" / "lightrag_webui",
        repo_root / "anything-chat-rag" / "lightrag_webui",
    ]
    for path in candidates:
        if (path / "package.json").exists():
            return path
    raise SystemExit(
        "Cannot find LightRAG WebUI project. Provide it via:\n"
        "- sum_mcp_server/vendor/lightrag_webui (standalone bundle)\n"
        "- or keep repo root 'anything-chat-rag/lightrag_webui' present."
    )


def _resolve_npm() -> str:
    npm = shutil.which("npm")
    if npm:
        return npm
    raise SystemExit("Cannot find 'npm' on PATH. Install Node.js (includes npm).")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="LightRAG WebUI dev server (Vite)")
    parser.add_argument("--host", type=str, default=os.environ.get("LIGHTRAG_WEBUI_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("LIGHTRAG_WEBUI_PORT", 9622)))
    parser.add_argument(
        "--mode",
        choices=["dev", "preview"],
        default=os.environ.get("LIGHTRAG_WEBUI_MODE", "dev"),
        help="dev=Vite dev server; preview=serve build output (requires build first)",
    )
    args = parser.parse_args(argv)

    repo_root = Path(__file__).resolve().parents[2]
    load_dotenv(repo_root / "sum_mcp_server" / ".env", override=False)
    load_dotenv(repo_root / ".env", override=False)

    webui_dir = _find_webui_dir(repo_root)
    npm = _resolve_npm()

    # Use npm scripts that don't require bun.
    script = "dev-no-bun" if args.mode == "dev" else "preview-no-bun"

    env = os.environ.copy()
    env.setdefault("VITE_API_PROXY", "true")
    env.setdefault("VITE_API_ENDPOINTS", "/api,/docs,/redoc,/openapi.json,/static")
    env.setdefault("VITE_BACKEND_URL", f"http://127.0.0.1:{os.environ.get('LIGHTRAG_API_PORT', '9621')}")

    cmd = [npm, "run", script, "--", "--host", str(args.host), "--port", str(args.port)]
    proc = subprocess.Popen(cmd, cwd=str(webui_dir), env=env)
    return int(proc.wait())


if __name__ == "__main__":
    raise SystemExit(main())

