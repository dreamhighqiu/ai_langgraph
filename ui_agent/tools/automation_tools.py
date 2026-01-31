import json
from typing import Any, Dict

from ui_agent.automation.script_generator import create_script_save_tool, create_java_suite_save_tool
from ui_agent.automation.executor import create_playwright_executor_tool
from ui_agent.automation.report_parser import create_result_parser_tool


def ui_save_playwright_script(script_content: str, script_name: str = "", language: str = "typescript") -> str:
    tool = create_script_save_tool()
    return tool.func(script_content=script_content, script_name=script_name, language=language)


def ui_save_playwright_java(java_code: str, class_name: str = "GeneratedTest", package_name: str = "") -> str:
    tool = create_java_suite_save_tool()
    return tool.func(java_code=java_code, class_name=class_name, package_name=package_name)


def ui_run_playwright_script(
    script_path: str,
    browser: str = "",
    headless: bool | None = None,
    reporter: str = "html,json",
) -> str:
    tool = create_playwright_executor_tool()
    return tool.func(script_path=script_path, browser=browser, headless=headless, reporter=reporter)


def ui_parse_test_results(result_file_path: str) -> str:
    tool = create_result_parser_tool()
    return tool.func(result_file_path=result_file_path)


def ui_parse_test_results_json(result_file_path: str) -> Dict[str, Any]:
    return json.loads(ui_parse_test_results(result_file_path))
