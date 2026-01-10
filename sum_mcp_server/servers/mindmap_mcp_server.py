"""
MindMap MCP 服务端（统一入口）

提供工具：
1) generate_mindmap: Markdown -> MindMap (HTML 或文件路径)
"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastmcp import FastMCP


mcp = FastMCP("MindMap MCP Server")


@mcp.tool()
async def generate_mindmap(
    markdown: str,
    return_type: str = "html",
    toolbar: bool = True,
    filename: Optional[str] = None,
) -> str:
    try:
        return _generate_via_markmap_cli(markdown, return_type, toolbar, filename)
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error generating mindmap: {exc}"


def _generate_via_markmap_cli(
    markdown: str,
    return_type: str,
    toolbar: bool,
    filename: Optional[str],
) -> str:
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(markdown)
            temp_md = tmp_file.name

        try:
            output_dir = Path(tempfile.gettempdir()) / "mindmaps"
            output_dir.mkdir(exist_ok=True)

            if filename is None:
                import time

                filename = f"mindmap_{int(time.time())}.html"

            output_path = output_dir / filename

            cmd = [
                "npx",
                "-y",
                "markmap-cli",
                temp_md,
                "-o",
                str(output_path),
            ]
            if not toolbar:
                cmd.append("--no-toolbar")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode != 0:
                return f"Error: {result.stderr}"

            html_content = output_path.read_text(encoding="utf-8")
            if return_type == "html":
                return html_content
            return str(output_path)
        finally:
            if os.path.exists(temp_md):
                os.unlink(temp_md)
    except FileNotFoundError:
        return "Error: npx 未找到。请安装 Node.js: https://nodejs.org/"
    except subprocess.TimeoutExpired:
        return "Error: 生成思维导图超时"
    except Exception as exc:  # pylint: disable=broad-except
        return f"Error: {exc}"


def parse_arguments():
    parser = argparse.ArgumentParser(description="MindMap MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MINDMAP_MCP_PORT", 8007)),
        help="Port for SSE transport (default: 8007)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default=os.environ.get("MINDMAP_MCP_HOST", "0.0.0.0"),
        help="Host for SSE transport (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--sse",
        action="store_true",
        default=True,
        help="Use SSE transport (default: True)",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_arguments()
    if args.sse:
        mcp.run(transport="sse", port=args.port, host=args.host)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

