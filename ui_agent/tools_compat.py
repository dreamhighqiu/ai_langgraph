from pathlib import Path

from ui_agent.tools.analysis_tools import ui_mcp_page_structure, ui_api_page_structure, ui_page_structure
from ui_agent.tools.locator_tools import ui_ai_locator_analysis
from ui_agent.tools.case_tools import ui_generate_test_cases
from ui_agent.tools.suite_tools import ui_generate_test_suite
from ui_agent.tools.codegen_tools import ui_playwright_codegen
from ui_agent.tools.maintenance_tools import ui_optimize_locators
from ui_agent.tools.pipeline_tools import ui_full_pipeline
from ui_agent.tools.automation_tools import (
    ui_save_playwright_script,
    ui_save_playwright_java,
    ui_run_playwright_script,
    ui_parse_test_results,
)
from ui_agent.tools.chrome_tools import ui_generate_test_suite_chrome_mcp

try:
    from langchain.tools import StructuredTool
except ImportError:
    StructuredTool = None


def _as_tool(func, name: str, description: str):
    if StructuredTool is None:
        return func
    return StructuredTool.from_function(func=func, name=name, description=description)


ui_tools = [
    _as_tool(
        ui_mcp_page_structure,
        name="ui_mcp_page_structure",
        description="Obtain page structure via Playwright MCP.",
    ),
    _as_tool(
        ui_api_page_structure,
        name="ui_api_page_structure",
        description="Obtain page structure via Playwright API (local).",
    ),
    _as_tool(
        ui_page_structure,
        name="ui_page_structure",
        description="Obtain page structure using configured mode with fallback.",
    ),
    _as_tool(
        ui_ai_locator_analysis,
        name="ui_ai_locator_analysis",
        description="AI locator analysis and Page Object generation.",
    ),
    _as_tool(
        ui_generate_test_cases,
        name="ui_generate_test_cases",
        description="Generate functional test cases from analysis data.",
    ),
    _as_tool(
        ui_generate_test_suite,
        name="ui_generate_test_suite",
        description="Generate Java UI automation suite (Test + Helper + Page Object).",
    ),
    _as_tool(
        ui_generate_test_suite_chrome_mcp,
        name="ui_generate_test_suite_chrome_mcp",
        description="Generate Playwright Java suite using Chrome MCP agent.",
    ),
    _as_tool(
        ui_playwright_codegen,
        name="ui_playwright_codegen",
        description="Run Playwright codegen for manual recording.",
    ),
    _as_tool(
        ui_optimize_locators,
        name="ui_optimize_locators",
        description="Optimize locators and generate maintenance report.",
    ),
    _as_tool(
        ui_full_pipeline,
        name="ui_full_pipeline",
        description="Run analysis, test case generation, and suite generation in one pipeline.",
    ),
    _as_tool(
        ui_save_playwright_script,
        name="ui_save_playwright_script",
        description="Save Playwright TypeScript/JavaScript test script into run directory.",
    ),
    _as_tool(
        ui_save_playwright_java,
        name="ui_save_playwright_java",
        description="Save Playwright Java test code into run directory.",
    ),
    _as_tool(
        ui_run_playwright_script,
        name="ui_run_playwright_script",
        description="Execute Playwright test script and generate report.",
    ),
    _as_tool(
        ui_parse_test_results,
        name="ui_parse_test_results",
        description="Parse Playwright test results JSON.",
    ),
]

