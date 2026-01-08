"""
MindMap MCP 服务器 - 思维导图生成服务

本 MCP 服务器提供思维导图生成功能，支持：
- Markdown 到思维导图的转换
- 多种输出格式（HTML、文件路径）
- 可配置的工具栏显示

主要工具：
1. generate_mindmap: 生成思维导图（返回 HTML 内容或文件路径）
"""

import argparse
import os
import tempfile
import subprocess
from pathlib import Path
from typing import Any, Optional
from dotenv import load_dotenv

from fastmcp import FastMCP

# 创建 FastMCP 实例
mcp = FastMCP("MindMap MCP Server")


@mcp.tool()
async def generate_mindmap(
    markdown: str,
    return_type: str = "html",
    toolbar: bool = True,
    filename: Optional[str] = None,
) -> str:
    """
    将 Markdown 内容转换为思维导图
    
    Args:
        markdown: 要转换的 Markdown 内容
        return_type: 返回类型，可选值：
            - "html": 返回完整的 HTML 内容（默认）
            - "filePath": 保存到文件并返回文件路径
        toolbar: 是否显示工具栏（默认：True）
        filename: 自定义文件名（仅在 return_type="filePath" 时有效）
    
    Returns:
        str: 如果 return_type="html"，返回 HTML 内容
             如果 return_type="filePath"，返回文件路径
    """
    try:
        # 使用 markmap-cli 生成思维导图
        # 首先尝试使用 npx markmap-cli（如果 Node.js 可用）
        return _generate_via_markmap_cli(markdown, return_type, toolbar, filename)
    
    except Exception as e:
        return f"Error generating mindmap: {str(e)}"


def _generate_via_markmap_cli(
    markdown: str,
    return_type: str,
    toolbar: bool,
    filename: Optional[str],
) -> str:
    """通过 markmap-cli 生成思维导图"""
    try:
        # 创建临时文件存储 markdown
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write(markdown)
            temp_md = f.name
        
        try:
            # 创建输出目录
            output_dir = Path(tempfile.gettempdir()) / "mindmaps"
            output_dir.mkdir(exist_ok=True)
            
            if filename is None:
                import time
                filename = f"mindmap_{int(time.time())}.html"
            
            output_path = output_dir / filename
            
            # 使用 npx markmap-cli 生成思维导图
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
            
            # 读取生成的 HTML
            html_content = output_path.read_text(encoding="utf-8")
            
            if return_type == "html":
                # 返回 HTML 内容
                return html_content
            else:
                # 返回文件路径
                return str(output_path)
        
        finally:
            # 清理临时文件
            if os.path.exists(temp_md):
                os.unlink(temp_md)
    
    except FileNotFoundError:
        return "Error: npx 未找到。请安装 Node.js: https://nodejs.org/"
    except subprocess.TimeoutExpired:
        return "Error: 生成思维导图超时"
    except Exception as e:
        return f"Error: {str(e)}"


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="MindMap MCP Server")
    parser.add_argument(
        "--port",
        type=int,
        default=int(os.environ.get("MINDMAP_MCP_PORT", 9003)),
        help="Port for SSE transport (default: 9003)",
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
    """主入口点"""
    load_dotenv()
    args = parse_arguments()
    
    print("MindMap MCP Server Configuration:")
    print(f"   Port: {args.port}")
    print(f"   Host: {args.host}")
    print(f"   Transport: SSE")
    
    if args.sse:
        mcp.run(transport="sse", port=args.port, host=args.host)
    else:
        mcp.run()


if __name__ == "__main__":
    main()

