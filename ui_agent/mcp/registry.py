from typing import Any, Dict, List

from ui_agent.core.config import get_config


def _build_playwright_mcp_config() -> Dict[str, Any]:
    cfg = get_config()
    mcp_cfg = cfg.get("analysis.mcp.playwright_mcp", {})
    command = mcp_cfg.get("command")
    if not command:
        raise RuntimeError(
            "Playwright MCP server is not configured. Set analysis.mcp.playwright_mcp.command."
        )

    return {
        "server_name": mcp_cfg.get("server_name", "playwright"),
        "transport": mcp_cfg.get("transport", "stdio"),
        "command": command,
        "args": mcp_cfg.get("args", []),
        "env": mcp_cfg.get("env", {}),
    }


def _build_chrome_mcp_config() -> Dict[str, Any]:
    cfg = get_config()
    chrome_cfg = cfg.get_section("chrome_mcp")
    url = chrome_cfg.get("url")
    transport = chrome_cfg.get("transport")
    if not url:
        raise RuntimeError("Chrome MCP is not configured. Set chrome_mcp.url.")
    if not transport:
        raise RuntimeError("Chrome MCP is not configured. Set chrome_mcp.transport.")

    return {
        "server_name": chrome_cfg.get("server_name", "midscene-web"),
        "transport": transport,
        "url": url,
    }


async def get_playwright_mcp_tools() -> List[Any]:
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as exc:
        raise RuntimeError("Missing dependency: langchain-mcp-adapters") from exc

    server_config = _build_playwright_mcp_config()
    server_name = server_config.pop("server_name")
    client = MultiServerMCPClient({server_name: server_config})
    return await client.get_tools()


async def get_chrome_mcp_tools() -> List[Any]:
    try:
        from langchain_mcp_adapters.client import MultiServerMCPClient
    except ImportError as exc:
        raise RuntimeError("Missing dependency: langchain-mcp-adapters") from exc

    server_config = _build_chrome_mcp_config()
    server_name = server_config.pop("server_name")
    client = MultiServerMCPClient({server_name: server_config})
    return await client.get_tools()
