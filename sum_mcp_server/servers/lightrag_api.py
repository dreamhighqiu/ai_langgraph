from __future__ import annotations

import runpy
import sys
from pathlib import Path


def _ensure_lightrag_on_path() -> None:
    repo_root = Path(__file__).resolve().parents[2]

    candidates = [
        repo_root / "sum_mcp_server" / "vendor",
        repo_root / "anything-chat-rag",
    ]
    for root in candidates:
        if (root / "lightrag").exists():
            sys.path.insert(0, str(root))
            return

    raise SystemExit(
        "Cannot find 'lightrag' package. Provide it via:\n"
        "- sum_mcp_server/vendor/lightrag (standalone bundle)\n"
        "- or keep repo root 'anything-chat-rag/lightrag' present."
    )


if __name__ == "__main__":
    _ensure_lightrag_on_path()
    # Run as module to preserve LightRAG's own CLI/argparse behavior.
    runpy.run_module("lightrag.api.lightrag_server", run_name="__main__")

