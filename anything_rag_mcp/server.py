from __future__ import annotations

"""
Compatibility shim.

Canonical implementation lives in `sum_mcp_server/servers/anything_rag_http_mcp.py`.
This file is kept to avoid breaking existing scripts that still run:
  python anything_rag_mcp/server.py ...
"""

import runpy
import sys
from pathlib import Path


if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(repo_root))
    runpy.run_path(str(repo_root / "sum_mcp_server" / "servers" / "anything_rag_http_mcp.py"), run_name="__main__")

