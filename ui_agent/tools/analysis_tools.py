from typing import Any, Dict, Optional

from ui_agent.core.config import get_config
from ui_agent.analysis.mcp.playwright_analyzer import MCPPlaywrightAnalyzer
from ui_agent.analysis.webpage_analyzer import WebpageAnalyzer
from ui_agent.tools.common import run_async, normalize_analysis


def ui_mcp_page_structure(url: str, output_dir: Optional[str] = None, screenshot: bool = True) -> Dict[str, Any]:
    """Obtain page structure via Playwright MCP."""
    analyzer = MCPPlaywrightAnalyzer()
    result = run_async(analyzer.analyze_url(url=url, output_dir=output_dir, screenshot=screenshot))
    payload = analyzer.to_dict(result)
    payload["raw_content"] = result.raw_content
    return normalize_analysis(payload)


def ui_api_page_structure(
    url: str,
    output_dir: Optional[str] = None,
    screenshot: bool = True,
    capture_network: bool = True,
    auth_state: Optional[str] = None,
) -> Dict[str, Any]:
    """Obtain page structure via Playwright API (local)."""
    config = get_config()
    playwright_cfg = config.get_section("playwright")
    headless = playwright_cfg.get("headless", True)
    timeout = playwright_cfg.get("timeout", 60000)

    analyzer = WebpageAnalyzer(headless=headless, timeout=timeout, auth_state=auth_state)
    result = analyzer.analyze(url=url, screenshot=screenshot, capture_network=capture_network, output_dir=output_dir)
    payload = analyzer.to_dict(result)
    return normalize_analysis(payload)


def ui_page_structure(
    url: str,
    output_dir: Optional[str] = None,
    screenshot: bool = True,
    allow_fallback: bool = True,
    auth_state: Optional[str] = None,
) -> Dict[str, Any]:
    """Obtain page structure using configured mode with optional fallback."""
    config = get_config()
    mode = config.get("analysis.mode", "mcp")

    if auth_state:
        return ui_api_page_structure(
            url=url,
            output_dir=output_dir,
            screenshot=screenshot,
            auth_state=auth_state,
        )

    if mode == "api":
        return ui_api_page_structure(
            url=url,
            output_dir=output_dir,
            screenshot=screenshot,
            auth_state=auth_state,
        )

    try:
        return ui_mcp_page_structure(url=url, output_dir=output_dir, screenshot=screenshot)
    except Exception:
        if not allow_fallback:
            raise
        return ui_api_page_structure(
            url=url,
            output_dir=output_dir,
            screenshot=screenshot,
            auth_state=auth_state,
        )
