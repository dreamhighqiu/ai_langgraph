from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    # Prefer vendored deps for standalone deployment.
    vendor_root = REPO_ROOT / "sum_mcp_server" / "vendor"
    if vendor_root.exists():
        sys.path.insert(0, str(vendor_root))
    anything_chat_rag_root = REPO_ROOT / "anything-chat-rag"
    if anything_chat_rag_root.exists():
        sys.path.insert(0, str(anything_chat_rag_root))
    from mcp_server_rag_anything.server import main  # noqa: E402

    main()
