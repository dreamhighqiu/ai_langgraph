"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

# server.py
from fastmcp import FastMCP
# pragma: no cover  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VRME5BPT06ZDE0MGFmYTk=

mcp = FastMCP("Demo 🚀")
# pylint: disable  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2T1VRME5BPT06ZDE0MGFmYTk=

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

if __name__ == "__main__":
    mcp.run(transport="sse", port=8000, host="0.0.0.0")