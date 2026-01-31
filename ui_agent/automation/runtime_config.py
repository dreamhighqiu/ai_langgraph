import os
from dataclasses import dataclass, field
from pathlib import Path

from ui_agent.core.config import get_config


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def _env_int(key: str, default: int = 0) -> int:
    return int(os.environ.get(key, str(default)))


def _env_bool(key: str, default: bool = False) -> bool:
    val = os.environ.get(key, "").lower()
    if val in ("true", "1", "yes"):
        return True
    if val in ("false", "0", "no"):
        return False
    return default


@dataclass
class AutomationRuntimeConfig:
    workspace_root: str = field(
        default_factory=lambda: _env(
            "UI_WORKSPACE_ROOT", str(Path(__file__).resolve().parents[2])
        )
    )

    chrome_mcp_url: str = field(
        default_factory=lambda: _env("CHROME_MCP_URL", "http://127.0.0.1:12306/mcp")
    )
    chrome_mcp_transport: str = field(
        default_factory=lambda: _env("CHROME_MCP_TRANSPORT", "streamable_http")
    )
    chrome_mcp_server_name: str = field(
        default_factory=lambda: _env("CHROME_MCP_SERVER_NAME", "midscene-web")
    )

    chart_mcp_command: str = field(
        default_factory=lambda: _env("CHART_MCP_COMMAND", "npx")
    )
    chart_mcp_args: list[str] = field(
        default_factory=lambda: ["-y", "@antv/mcp-server-chart"]
    )

    playwright_binary: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_BINARY", "npx")
    )
    playwright_args: list[str] = field(
        default_factory=lambda: ["playwright", "test"]
    )

    scripts_dir: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_SCRIPTS_DIR", "/playwright_scripts/tests")
    )
    results_dir: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_RESULTS_DIR", "/playwright_results")
    )
    reports_dir: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_REPORTS_DIR", "/playwright_reports")
    )
    base64_images_dir: str = field(
        default_factory=lambda: _env("BASE64_IMAGES_DIR", "/base64_images")
    )
    java_suites_dir: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_JAVA_SUITES_DIR", "/playwright_java")
    )

    default_browser: str = field(
        default_factory=lambda: _env("PLAYWRIGHT_DEFAULT_BROWSER", "chromium")
    )
    default_headless: bool = field(
        default_factory=lambda: _env_bool("PLAYWRIGHT_DEFAULT_HEADLESS", True)
    )
    default_timeout: int = field(
        default_factory=lambda: _env_int("PLAYWRIGHT_DEFAULT_TIMEOUT", 30000)
    )

    report_format: str = field(
        default_factory=lambda: _env("REPORT_FORMAT", "html")
    )
    include_screenshots: bool = field(
        default_factory=lambda: _env_bool("REPORT_INCLUDE_SCREENSHOTS", True)
    )
    include_videos: bool = field(
        default_factory=lambda: _env_bool("REPORT_INCLUDE_VIDEOS", False)
    )


def get_runtime_config() -> AutomationRuntimeConfig:
    cfg = get_config()
    chrome_cfg = cfg.get_section("chrome_mcp")
    chart_cfg = cfg.get_section("chart_mcp")
    automation_cfg = cfg.get_section("automation")

    runtime = AutomationRuntimeConfig()
    runtime.workspace_root = automation_cfg.get("workspace_root", runtime.workspace_root)
    runtime.chrome_mcp_url = chrome_cfg.get("url", runtime.chrome_mcp_url)
    runtime.chrome_mcp_transport = chrome_cfg.get(
        "transport", runtime.chrome_mcp_transport
    )
    runtime.chrome_mcp_server_name = chrome_cfg.get(
        "server_name", runtime.chrome_mcp_server_name
    )
    runtime.chart_mcp_command = chart_cfg.get("command", runtime.chart_mcp_command)
    runtime.chart_mcp_args = chart_cfg.get("args", runtime.chart_mcp_args)
    runtime.playwright_binary = automation_cfg.get(
        "playwright_binary", runtime.playwright_binary
    )
    runtime.playwright_args = automation_cfg.get(
        "playwright_args", runtime.playwright_args
    )
    runtime.scripts_dir = automation_cfg.get("scripts_dir", runtime.scripts_dir)
    runtime.results_dir = automation_cfg.get("results_dir", runtime.results_dir)
    runtime.reports_dir = automation_cfg.get("reports_dir", runtime.reports_dir)
    runtime.base64_images_dir = automation_cfg.get(
        "base64_images_dir", runtime.base64_images_dir
    )
    runtime.java_suites_dir = automation_cfg.get(
        "java_suites_dir", runtime.java_suites_dir
    )
    runtime.default_browser = automation_cfg.get(
        "default_browser", runtime.default_browser
    )
    runtime.default_headless = automation_cfg.get(
        "default_headless", runtime.default_headless
    )
    runtime.default_timeout = automation_cfg.get(
        "default_timeout", runtime.default_timeout
    )
    return runtime
