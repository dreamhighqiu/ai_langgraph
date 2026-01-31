"""Playwright script execution tool.

Key behaviors:
- Each execution is isolated into a per-run directory under `playwright_reports/report_<run_id>`.
- The HTML report is generated into that same directory (so it's never empty).
- Screenshots/traces/videos/etc. are written under `artifacts/` inside the run directory.
- The test script is copied into `playwright_scripts/tests` before running.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any

from langchain_core.tools import BaseTool, StructuredTool

from ui_automation.config import DEFAULT_CONFIG, UIAutomationConfig
from ui_automation.run_storage import (
    build_run_layout,
    extract_run_id,
    generate_run_id,
    set_current_run_id,
    join_virtual,
    resolve_virtual_path,
    sanitize_basename,
    to_posix_path,
)


def create_playwright_executor_tool(config: UIAutomationConfig | None = None) -> BaseTool:
    cfg = config or DEFAULT_CONFIG

    def run_playwright_script(
        script_path: str,
        browser: str = "",
        headless: bool | None = None,
        reporter: str = "html,json",
    ) -> str:
        actual_script_path = resolve_virtual_path(script_path, cfg.workspace_root)
        if not actual_script_path.exists():
            return json.dumps(
                {
                    "success": False,
                    "error": f"脚本文件不存在: {script_path}",
                    "actual_path": str(actual_script_path),
                },
                ensure_ascii=False,
                indent=2,
            )

        run_id = (
            extract_run_id(actual_script_path.name)
            or extract_run_id(str(actual_script_path.parent))
            or generate_run_id()
        )
        set_current_run_id(cfg, run_id)
        layout = build_run_layout(cfg, run_id)
        layout.run_dir_actual.mkdir(parents=True, exist_ok=True)
        layout.report_dir_actual.mkdir(parents=True, exist_ok=True)
        layout.artifacts_dir_actual.mkdir(parents=True, exist_ok=True)

        # Ensure the script is present in the run directory too (for auditing/debugging).
        run_script_name = actual_script_path.name
        if not extract_run_id(run_script_name):
            base = sanitize_basename(run_script_name)
            ext = ""
            if base.endswith(".spec.ts"):
                base = base[: -len(".spec.ts")]
                ext = ".spec.ts"
            elif base.endswith(".spec.js"):
                base = base[: -len(".spec.js")]
                ext = ".spec.js"
            if not base:
                base = "test"
            if not ext:
                ext = ".spec.ts"
            run_script_name = f"{base}_{run_id}{ext}"

        run_script_actual = layout.run_dir_actual / run_script_name
        if run_script_actual.resolve() != actual_script_path.resolve():
            run_script_actual.write_bytes(actual_script_path.read_bytes())

        playwright_project_dir = _find_playwright_project_dir(cfg, actual_script_path)
        tests_dir = playwright_project_dir / "tests"
        tests_dir.mkdir(parents=True, exist_ok=True)

        executable_script_actual = tests_dir / run_script_name
        executable_script_actual.write_bytes(run_script_actual.read_bytes())
        executable_script_virtual = join_virtual(cfg.scripts_dir, run_script_name)

        # Prepare a run-specific Playwright config under playwright_scripts, so module resolution works.
        run_config_path = _write_run_config(
            playwright_project_dir=playwright_project_dir,
            report_dir_actual=layout.report_dir_actual,
            artifacts_dir_actual=layout.artifacts_dir_actual,
            json_output_file_actual=layout.result_json_actual,
        )

        # Build Playwright command
        playwright_binary = cfg.playwright_binary
        if platform.system() == "Windows" and playwright_binary == "npx":
            playwright_binary = "npx.cmd"

        cmd = [playwright_binary] + cfg.playwright_args
        cmd.extend(["-c", str(run_config_path)])

        browser_type = browser or cfg.default_browser
        cmd.extend(["--project", browser_type])

        is_headless = headless if headless is not None else cfg.default_headless
        if not is_headless:
            cmd.append("--headed")

        # Force at least html+json for non-empty report + machine-readable result.
        requested_reporters = [r.strip() for r in (reporter or "").split(",") if r.strip()]
        reporter_used = ",".join(sorted(set(requested_reporters + ["html", "json"])))

        # Only run the single file we prepared in tests/.
        # Note: `--project` accepts multiple values, so we must use `--` to end option parsing.
        cmd.append("--")
        try:
            relative_script = executable_script_actual.relative_to(playwright_project_dir)
            cmd.append(str(relative_script).replace("\\", "/"))
        except ValueError:
            cmd.append(str(executable_script_actual).replace("\\", "/"))

        env = os.environ.copy()
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=600,
                cwd=str(playwright_project_dir),
                env=env,
            )
        except subprocess.TimeoutExpired:
            return json.dumps(
                {
                    "success": False,
                    "error": "Playwright 执行超时（10分钟）",
                    "script_path": script_path,
                    "run_id": run_id,
                    "run_dir": layout.run_dir_virtual,
                },
                ensure_ascii=False,
                indent=2,
            )
        except FileNotFoundError:
            return json.dumps(
                {
                    "success": False,
                    "error": f"Playwright 未安装或路径错误: {cfg.playwright_binary}",
                    "script_path": script_path,
                    "run_id": run_id,
                    "run_dir": layout.run_dir_virtual,
                },
                ensure_ascii=False,
                indent=2,
            )
        except Exception as exc:
            return json.dumps(
                {
                    "success": False,
                    "error": str(exc),
                    "script_path": script_path,
                    "run_id": run_id,
                    "run_dir": layout.run_dir_virtual,
                },
                ensure_ascii=False,
                indent=2,
            )

        # Copy result json into the legacy global results dir for backward compatibility.
        global_result_virtual = join_virtual(cfg.results_dir, f"result_{run_id}.json")
        global_result_actual = resolve_virtual_path(global_result_virtual, cfg.workspace_root)
        if layout.result_json_actual.exists():
            global_result_actual.parent.mkdir(parents=True, exist_ok=True)
            global_result_actual.write_bytes(layout.result_json_actual.read_bytes())

        index_html = layout.report_dir_actual / "index.html"
        html_report_ok = index_html.exists()

        # Convenience entrypoint: keep `/playwright_reports/report_<run_id>/index.html`
        # as a stable path that redirects to `/report/index.html`.
        root_index = layout.run_dir_actual / "index.html"
        if html_report_ok:
            try:
                root_index.write_text(
                    "<!doctype html><meta charset=\"utf-8\" />"
                    "<meta http-equiv=\"refresh\" content=\"0; url=./report/index.html\" />"
                    "<title>Playwright Report</title>",
                    encoding="utf-8",
                )
            except Exception:
                pass

        output: dict[str, Any] = {
            "success": result.returncode == 0,
            "run_id": run_id,
            "run_dir": layout.run_dir_virtual,
            "script_path": script_path,
            "executed_script": executable_script_virtual,
            "browser": browser_type,
            "headless": is_headless,
            "reporter_requested": reporter,
            "reporter_used": reporter_used,
            "json_result_run": join_virtual(layout.run_dir_virtual, layout.result_json_actual.name)
            if layout.result_json_actual.exists()
            else None,
            "json_result_global": global_result_virtual if global_result_actual.exists() else None,
            "html_report_dir": layout.report_dir_virtual,
            "html_report_index": join_virtual(layout.report_dir_virtual, "index.html") if html_report_ok else None,
            "html_report_root_index": join_virtual(layout.run_dir_virtual, "index.html") if html_report_ok else None,
            "artifacts_dir": join_virtual(layout.run_dir_virtual, "artifacts"),
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

        if layout.result_json_actual.exists():
            try:
                with open(layout.result_json_actual, "r", encoding="utf-8") as f:
                    test_results = json.load(f)
                output["summary"] = _extract_summary(test_results)
            except Exception as exc:
                output["parse_error"] = str(exc)

        return json.dumps(output, ensure_ascii=False, indent=2)

    return StructuredTool.from_function(
        name="run_playwright_script",
        func=run_playwright_script,
        description=(
            "执行 Playwright 测试脚本（会按单次对话/run隔离输出目录）。\n"
            "参数:\n"
            "- script_path: 脚本虚拟路径（如 /playwright_scripts/tests/test_xxx.spec.ts 或 /playwright_reports/report_xxx/test_xxx.spec.ts）\n"
            "- browser: chromium/firefox/webkit（可选）\n"
            "- headless: 是否无头（可选，默认按配置）\n"
            "- reporter: 期望 reporter（可选，默认 html,json；实际会强制包含 html+json 以保证报告不为空）\n"
            "返回: JSON（包含 run_dir/report/index.html、result.json、artifacts 目录等路径）。"
        ),
    )


def _find_playwright_project_dir(cfg: UIAutomationConfig, actual_script_path: Path) -> Path:
    parts = list(actual_script_path.resolve().parts)
    if "playwright_scripts" in parts:
        idx = parts.index("playwright_scripts")
        return Path(*parts[: idx + 1])

    candidate = Path(cfg.workspace_root).resolve() / "playwright_scripts"
    if candidate.exists():
        return candidate

    raise FileNotFoundError(f"playwright_scripts directory not found (workspace_root={cfg.workspace_root})")


def _write_run_config(
    playwright_project_dir: Path,
    report_dir_actual: Path,
    artifacts_dir_actual: Path,
    json_output_file_actual: Path,
) -> Path:
    config_dir = playwright_project_dir / ".run_configs"
    config_dir.mkdir(parents=True, exist_ok=True)

    # Use a stable filename so repeated retries reuse the same config for the same run dir.
    # Note: run_id is embedded in the run_dir name already; use the folder name here too.
    config_path = config_dir / f"{report_dir_actual.parent.name}.config.cjs"

    report_dir_posix = to_posix_path(report_dir_actual)
    artifacts_dir_posix = to_posix_path(artifacts_dir_actual)
    json_output_posix = to_posix_path(json_output_file_actual)

    # Config file must live under playwright_scripts so `@playwright/test` resolves from node_modules.
    config_content = f"""\
const path = require('path');
const {{ defineConfig, devices }} = require('@playwright/test');

module.exports = defineConfig({{
  testDir: path.resolve(__dirname, '..', 'tests'),
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  outputDir: {json.dumps(artifacts_dir_posix)},
  reporter: [
    ['html', {{ outputFolder: {json.dumps(report_dir_posix)}, open: 'never' }}],
    ['json', {{ outputFile: {json.dumps(json_output_posix)} }}],
  ],
  use: {{
    trace: 'on-first-retry',
  }},
  projects: [
    {{ name: 'chromium', use: {{ ...devices['Desktop Chrome'] }} }},
    {{ name: 'firefox', use: {{ ...devices['Desktop Firefox'] }} }},
    {{ name: 'webkit', use: {{ ...devices['Desktop Safari'] }} }},
  ],
}});
"""

    config_path.write_text(config_content, encoding="utf-8")
    return config_path


def _extract_summary(test_results: dict[str, Any]) -> dict[str, Any]:
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration": 0,
    }

    if "suites" in test_results:
        for suite in test_results.get("suites", []):
            _count_tests(suite, summary)

    if "stats" in test_results:
        stats = test_results["stats"]
        summary.update(
            {
                "total": stats.get("expected", 0) + stats.get("unexpected", 0) + stats.get("skipped", 0),
                "passed": stats.get("expected", 0),
                "failed": stats.get("unexpected", 0),
                "skipped": stats.get("skipped", 0),
                "duration": stats.get("duration", 0),
            }
        )

    return summary


def _count_tests(suite: dict[str, Any], summary: dict[str, Any]) -> None:
    for spec in suite.get("specs", []):
        for test in spec.get("tests", []):
            summary["total"] += 1
            for result in test.get("results", []):
                status = result.get("status", "")
                if status == "passed":
                    summary["passed"] += 1
                elif status == "failed":
                    summary["failed"] += 1
                elif status == "skipped":
                    summary["skipped"] += 1
                summary["duration"] += result.get("duration", 0)

    for sub_suite in suite.get("suites", []):
        _count_tests(sub_suite, summary)
