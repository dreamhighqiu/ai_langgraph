import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from ui_agent.tools import (
    ui_page_structure,
    ui_generate_test_cases,
    ui_generate_test_suite,
    ui_full_pipeline,
    ui_generate_test_suite_chrome_mcp,
    ui_save_playwright_script,
    ui_save_playwright_java,
    ui_run_playwright_script,
    ui_parse_test_results,
    ui_playwright_codegen,
)
from ui_agent.core.config import get_config
from ui_agent.tools.common import default_output_dir
from ui_agent.analysis.webpage_analyzer import WebpageAnalyzer


def _print_json(payload) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _validate_openai() -> Optional[str]:
    config = get_config()
    openai_cfg = config.get_section("openai")
    if not openai_cfg.get("api_key"):
        return "Missing openai.api_key"
    if not openai_cfg.get("model"):
        return "Missing openai.model"
    return None


def _validate_mcp() -> Optional[str]:
    config = get_config()
    mcp_cfg = config.get("analysis.mcp.playwright_mcp", {})
    if not mcp_cfg.get("command"):
        return "Missing analysis.mcp.playwright_mcp.command"
    return None


def _validate_chrome_mcp() -> Optional[str]:
    config = get_config()
    chrome_cfg = config.get_section("chrome_mcp")
    if not chrome_cfg.get("url"):
        return "Missing chrome_mcp.url"
    if not chrome_cfg.get("transport"):
        return "Missing chrome_mcp.transport"
    return None


def _check_dependency(module: str) -> bool:
    try:
        __import__(module)
        return True
    except Exception:
        return False


def cmd_analyze(args: argparse.Namespace) -> int:
    if args.auth_state and args.mode == "mcp":
        print("Auth state requires API mode. Switching to --mode api.", file=sys.stderr)
        args.mode = "api"

    if args.mode == "mcp":
        error = _validate_mcp()
        if error:
            print(error, file=sys.stderr)
            return 2

    config = get_config()
    if args.mode:
        config.config.setdefault("analysis", {})
        config.config["analysis"]["mode"] = args.mode

    output_dir = args.output_dir or str(default_output_dir("analysis"))
    analysis = ui_page_structure(
        url=args.url,
        output_dir=output_dir,
        screenshot=not args.no_screenshot,
        allow_fallback=not args.no_fallback,
        auth_state=args.auth_state,
    )
    if args.output:
        Path(args.output).write_text(
            json.dumps(analysis, indent=2, ensure_ascii=False), encoding="utf-8"
        )
    else:
        _print_json(analysis)
    return 0


def cmd_cases(args: argparse.Namespace) -> int:
    if args.auth_state and args.mode == "mcp":
        print("Auth state requires API mode. Switching to --mode api.", file=sys.stderr)
        args.mode = "api"

    if args.mode == "mcp":
        error = _validate_mcp()
        if error:
            print(error, file=sys.stderr)
            return 2
    if args.use_ai:
        error = _validate_openai()
        if error:
            print(error, file=sys.stderr)
            return 2

    config = get_config()
    if args.mode:
        config.config.setdefault("analysis", {})
        config.config["analysis"]["mode"] = args.mode

    analysis = ui_page_structure(
        url=args.url,
        output_dir=args.output_dir,
        screenshot=not args.no_screenshot,
        allow_fallback=not args.no_fallback,
        auth_state=args.auth_state,
    )
    formats = args.format.split(",") if args.format else ["json", "excel"]
    result = ui_generate_test_cases(
        analysis=analysis,
        output_path=args.output,
        use_ai=args.use_ai,
        reference_cases_path=args.reference_cases,
        export_formats=formats,
        export_path=args.export_path,
    )
    _print_json(result)
    return 0


def cmd_suite(args: argparse.Namespace) -> int:
    error = _validate_openai()
    if error:
        print(error, file=sys.stderr)
        return 2

    result = ui_generate_test_suite(
        url=args.url,
        auth_state=args.auth_state,
        reference_test_path=args.reference_test,
        reference_page_path=args.reference_page,
        output_dir=args.output_dir,
    )
    _print_json(result)
    return 0


def cmd_chrome_suite(args: argparse.Namespace) -> int:
    result = ui_generate_test_suite_chrome_mcp(
        url=args.url,
        prompt=args.prompt,
        debug=args.debug,
    )
    _print_json(result)
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    if args.auth_state and args.mode == "mcp":
        print("Auth state requires API mode. Switching to --mode api.", file=sys.stderr)
        args.mode = "api"

    if args.mode == "mcp":
        error = _validate_mcp()
        if error:
            print(error, file=sys.stderr)
            return 2
    if args.use_ai_cases:
        error = _validate_openai()
        if error:
            print(error, file=sys.stderr)
            return 2
    config = get_config()
    if args.mode:
        config.config.setdefault("analysis", {})
        config.config["analysis"]["mode"] = args.mode
    formats = args.cases_format.split(",") if args.cases_format else ["json", "excel"]
    result = ui_full_pipeline(
        url=args.url,
        auth_state=args.auth_state,
        reference_test_path=args.reference_test,
        reference_page_path=args.reference_page,
        use_ai_cases=args.use_ai_cases,
        reference_cases_path=args.reference_cases,
        case_export_formats=formats,
        case_export_path=args.cases_export_path,
        optimize_code_path=args.optimize_code_path,
        optimize_language=args.optimize_language,
        optimize_report=not args.no_optimize_report,
        output_dir=args.output_dir,
    )
    _print_json(result)
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if not args.check_openai and not args.check_mcp:
        args.check_openai = True
        args.check_mcp = True

    results = {
        "openai": None,
        "mcp": None,
        "chrome_mcp": None,
        "deps": {
            "openai": _check_dependency("openai"),
            "playwright": _check_dependency("playwright"),
            "langchain": _check_dependency("langchain"),
            "langchain_mcp_adapters": _check_dependency("langchain_mcp_adapters"),
            "yaml": _check_dependency("yaml"),
            "deepagents": _check_dependency("deepagents"),
            "langgraph": _check_dependency("langgraph"),
        },
    }

    if args.check_openai:
        results["openai"] = _validate_openai()
    if args.check_mcp:
        results["mcp"] = _validate_mcp()
    if args.check_chrome_mcp:
        results["chrome_mcp"] = _validate_chrome_mcp()

    _print_json(results)
    return 0


def cmd_login(args: argparse.Namespace) -> int:
    config = get_config()
    playwright_cfg = config.get_section("playwright")
    headless = playwright_cfg.get("headless", True)
    timeout = playwright_cfg.get("timeout", 60000)

    analyzer = WebpageAnalyzer(headless=False, timeout=timeout)
    analyzer.save_auth_state(
        storage_path=args.output,
        login_url=args.url,
        timeout_ms=args.timeout,
        wait_until=args.wait_until,
    )
    return 0


def cmd_script_save(args: argparse.Namespace) -> int:
    output = ui_save_playwright_script(
        script_content=Path(args.file).read_text(encoding="utf-8"),
        script_name=args.name or Path(args.file).stem,
        language=args.language,
    )
    print(output)
    return 0


def cmd_script_run(args: argparse.Namespace) -> int:
    output = ui_run_playwright_script(
        script_path=args.script_path,
        browser=args.browser,
        headless=None if args.headless is None else args.headless.lower() == "true",
        reporter=args.reporter,
    )
    print(output)
    return 0


def cmd_result_parse(args: argparse.Namespace) -> int:
    output = ui_parse_test_results(args.result_path)
    print(output)
    return 0


def cmd_codegen(args: argparse.Namespace) -> int:
    output = ui_playwright_codegen(
        url=args.url,
        output_path=args.output,
        language=args.language,
    )
    _print_json(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="ui_agent", description="UI agent CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    analyze = sub.add_parser("analyze", help="Analyze page structure")
    analyze.add_argument("--url", required=True)
    analyze.add_argument("--output-dir")
    analyze.add_argument("--output", help="Write analysis JSON to file")
    analyze.add_argument("--mode", choices=["mcp", "api"], default=None)
    analyze.add_argument("--auth-state", help="Storage state JSON for login session")
    analyze.add_argument("--no-screenshot", action="store_true")
    analyze.add_argument("--no-fallback", action="store_true")
    analyze.set_defaults(func=cmd_analyze)

    cases = sub.add_parser("cases", help="Generate functional test cases")
    cases.add_argument("--url", required=True)
    cases.add_argument("--output-dir")
    cases.add_argument("--output", help="Write cases JSON to file")
    cases.add_argument("--use-ai", action="store_true")
    cases.add_argument("--reference-cases")
    cases.add_argument("--format", help="Comma-separated: json,excel,xmind")
    cases.add_argument("--export-path", help="Base path for exported case files")
    cases.add_argument("--mode", choices=["mcp", "api"], default=None)
    cases.add_argument("--auth-state", help="Storage state JSON for login session")
    cases.add_argument("--no-screenshot", action="store_true")
    cases.add_argument("--no-fallback", action="store_true")
    cases.set_defaults(func=cmd_cases)

    suite = sub.add_parser("suite", help="Generate Java PageObject + Helper + Test")
    suite.add_argument("--url", required=True)
    suite.add_argument("--output-dir")
    suite.add_argument("--auth-state")
    suite.add_argument("--reference-test")
    suite.add_argument("--reference-page")
    suite.set_defaults(func=cmd_suite)

    chrome_suite = sub.add_parser("chrome-suite", help="Generate Java suite via Chrome MCP agent")
    chrome_suite.add_argument("--url", required=True)
    chrome_suite.add_argument("--prompt")
    chrome_suite.add_argument("--debug", action="store_true")
    chrome_suite.set_defaults(func=cmd_chrome_suite)

    pipeline = sub.add_parser("pipeline", help="Run full pipeline")
    pipeline.add_argument("--url", required=True)
    pipeline.add_argument("--output-dir")
    pipeline.add_argument("--auth-state")
    pipeline.add_argument("--reference-test")
    pipeline.add_argument("--reference-page")
    pipeline.add_argument("--use-ai-cases", action="store_true")
    pipeline.add_argument("--reference-cases")
    pipeline.add_argument("--mode", choices=["mcp", "api"], default=None)
    pipeline.add_argument("--optimize-code-path")
    pipeline.add_argument("--optimize-language", default="java")
    pipeline.add_argument("--no-optimize-report", action="store_true")
    pipeline.add_argument("--cases-format", help="Comma-separated: json,excel,xmind")
    pipeline.add_argument("--cases-export-path", help="Base path for exported case files")
    pipeline.set_defaults(func=cmd_pipeline)

    validate = sub.add_parser("validate", help="Validate config and dependencies")
    validate.add_argument("--check-openai", action="store_true")
    validate.add_argument("--check-mcp", action="store_true")
    validate.add_argument("--check-chrome-mcp", action="store_true")
    validate.set_defaults(func=cmd_validate)

    script_save = sub.add_parser("script-save", help="Save Playwright script into run directory")
    script_save.add_argument("--file", required=True, help="Path to script file")
    script_save.add_argument("--name", help="Script name override")
    script_save.add_argument("--language", choices=["typescript", "javascript"], default="typescript")
    script_save.set_defaults(func=cmd_script_save)

    script_run = sub.add_parser("script-run", help="Run Playwright script by virtual path")
    script_run.add_argument("--script-path", required=True, help="Virtual script path")
    script_run.add_argument("--browser", default="")
    script_run.add_argument("--headless", help="true/false")
    script_run.add_argument("--reporter", default="html,json")
    script_run.set_defaults(func=cmd_script_run)

    result_parse = sub.add_parser("result-parse", help="Parse Playwright test results JSON")
    result_parse.add_argument("--result-path", required=True, help="Virtual result JSON path")
    result_parse.set_defaults(func=cmd_result_parse)

    codegen = sub.add_parser("codegen", help="Record script via Playwright codegen")
    codegen.add_argument("--url", required=True)
    codegen.add_argument("--output", help="Output file path")
    codegen.add_argument("--language", default="java", help="python/javascript/typescript/java")
    codegen.set_defaults(func=cmd_codegen)

    login = sub.add_parser("login", help="Manual login and save storage state")
    login.add_argument("--url", help="Login URL override")
    login.add_argument("--output", default="./auth_state.json", help="Storage state output path")
    login.add_argument("--timeout", type=int, default=90000, help="Goto timeout in ms (default 90000)")
    login.add_argument(
        "--wait-until",
        default="domcontentloaded",
        choices=["load", "domcontentloaded", "networkidle", "commit"],
        help="Navigation wait strategy",
    )
    login.set_defaults(func=cmd_login)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
