import json
from pathlib import Path
from typing import Any

from langchain_core.tools import StructuredTool, BaseTool

from ui_agent.automation.runtime_config import get_runtime_config


def _resolve_virtual_path(virtual_path: str, workspace_root: str) -> Path:
    relative_path = virtual_path.lstrip("/")
    return Path(workspace_root).resolve() / relative_path


def create_result_parser_tool() -> BaseTool:
    cfg = get_runtime_config()

    def parse_test_results(result_file_path: str) -> str:
        actual_path = _resolve_virtual_path(result_file_path, cfg.workspace_root)

        if not actual_path.exists():
            return json.dumps(
                {
                    "success": False,
                    "error": f"Result file not found: {result_file_path}",
                    "actual_path": str(actual_path),
                },
                ensure_ascii=False,
                indent=2,
            )

        try:
            with open(actual_path, "r", encoding="utf-8") as f:
                raw_results = json.load(f)

            parsed = {
                "success": True,
                "result_file": result_file_path,
                "summary": _extract_summary(raw_results),
                "test_cases": _extract_test_cases(raw_results),
                "errors": _extract_errors(raw_results),
            }

            return json.dumps(parsed, ensure_ascii=False, indent=2)

        except json.JSONDecodeError as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"JSON decode error: {str(e)}",
                    "result_file": result_file_path,
                },
                ensure_ascii=False,
                indent=2,
            )
        except Exception as e:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Parse error: {str(e)}",
                    "result_file": result_file_path,
                },
                ensure_ascii=False,
                indent=2,
            )

    return StructuredTool.from_function(
        name="parse_test_results",
        func=parse_test_results,
        description=(
            "Parse Playwright test results JSON.\n"
            "Args:\n"
            "- result_file_path: virtual path (e.g. /playwright_results/result_xxx.json)\n"
            "Returns JSON with summary and per-test details."
        ),
    )


def _extract_summary(results: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "flaky": 0,
        "duration_ms": 0,
        "workers": results.get("config", {}).get("workers", 1),
    }

    if "stats" in results:
        stats = results["stats"]
        summary.update(
            {
                "total": stats.get("expected", 0)
                + stats.get("unexpected", 0)
                + stats.get("skipped", 0)
                + stats.get("flaky", 0),
                "passed": stats.get("expected", 0),
                "failed": stats.get("unexpected", 0),
                "skipped": stats.get("skipped", 0),
                "flaky": stats.get("flaky", 0),
                "duration_ms": stats.get("duration", 0),
            }
        )

    return summary


def _extract_test_cases(results: dict[str, Any]) -> list[dict[str, Any]]:
    test_cases: list[dict[str, Any]] = []

    for suite in results.get("suites", []):
        _collect_test_cases(suite, test_cases, [])

    return test_cases


def _collect_test_cases(suite: dict, test_cases: list, parent_titles: list) -> None:
    current_titles = parent_titles + [suite.get("title", "")]

    for spec in suite.get("specs", []):
        file_path = spec.get("file", "")
        line = spec.get("line", 0)
        column = spec.get("column", 0)

        for test in spec.get("tests", []):
            test_title = test.get("title", "")
            full_title = " > ".join(current_titles + [test_title])

            for result in test.get("results", []):
                test_case = {
                    "title": test_title,
                    "full_title": full_title,
                    "file": file_path,
                    "line": line,
                    "column": column,
                    "status": result.get("status", "unknown"),
                    "duration_ms": result.get("duration", 0),
                    "retry": result.get("retry", 0),
                    "error": result.get("error", {}).get("message") if result.get("error") else None,
                    "attachments": len(result.get("attachments", [])),
                }
                test_cases.append(test_case)

    for sub_suite in suite.get("suites", []):
        _collect_test_cases(sub_suite, test_cases, current_titles)


def _extract_errors(results: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []

    for suite in results.get("suites", []):
        _collect_errors(suite, errors)

    return errors


def _collect_errors(suite: dict, errors: list) -> None:
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            for result in test.get("results", []):
                if result.get("status") in ["failed", "timedOut"]:
                    error_info = {
                        "test": test.get("title", ""),
                        "file": spec.get("file", ""),
                        "status": result.get("status", ""),
                        "error_message": result.get("error", {}).get("message", ""),
                        "error_stack": result.get("error", {}).get("stack", ""),
                    }
                    errors.append(error_info)
