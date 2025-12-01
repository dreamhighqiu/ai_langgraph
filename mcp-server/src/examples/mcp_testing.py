

# server.py
from fastmcp import FastMCP
# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWtaT2NRPT06NDAwNjU3YjM=

mcp = FastMCP("Demo 🚀")

@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
# fmt: off  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TWtaT2NRPT06NDAwNjU3YjM=

if __name__ == "__main__":
    mcp.run(transport="sse", port=8000, host="0.0.0.0")