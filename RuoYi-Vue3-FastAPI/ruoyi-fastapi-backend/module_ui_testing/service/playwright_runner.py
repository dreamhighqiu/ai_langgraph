"""
Playwright UI automation runner.

This module provides a minimal, dependency-light implementation based on
`testing-agents-service/src/ui_automation/tools/*`:
- Save generated Playwright test script into a run-scoped folder
- Copy it into `testing-agents-service/playwright_scripts/tests` for execution
- Execute via `npx playwright test` with a run-specific config that outputs:
  - HTML report into the run folder
  - JSON results into the run folder (for parsing/metrics)
"""

from __future__ import annotations

import io
import json
import os
import platform
import re
import subprocess
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


RUN_ID_PATTERN = re.compile(r"(\d{8}_\d{6}_[0-9a-fA-F]{8})")


def generate_run_id(now: Optional[datetime] = None) -> str:
    timestamp = (now or datetime.now()).strftime("%Y%m%d_%H%M%S")
    import uuid

    suffix = uuid.uuid4().hex[:8]
    return f"{timestamp}_{suffix}"


def sanitize_basename(name: str) -> str:
    name = (name or "").strip()
    if not name:
        return ""
    name = re.sub(r"[^\w.\-]+", "_", name, flags=re.UNICODE)
    return name.strip("._-")


def to_posix_path(path: Path) -> str:
    return str(path.resolve()).replace("\\", "/")


@dataclass(frozen=True)
class PlaywrightRunLayout:
    run_id: str
    run_dir: Path
    report_dir: Path
    artifacts_dir: Path
    result_json: Path
    script_in_run: Path
    script_in_tests: Path
    run_config_path: Path


class PlaywrightRunner:
    """
    Execute Playwright tests using the Node project under `testing-agents-service/playwright_scripts`.
    """

    def __init__(self, workspace_root: Optional[Path] = None) -> None:
        # Default to repo_root/testing-agents-service
        if workspace_root is None:
            # .../RuoYi-Vue3-FastAPI/ruoyi-fastapi-backend/module_ui_testing/service/playwright_runner.py
            repo_root = Path(__file__).resolve().parents[4]
            workspace_root = repo_root / "testing-agents-service"

        env_root = os.getenv("UI_AUTOMATION_WORKSPACE_ROOT")
        if env_root:
            workspace_root = Path(env_root)

        self.workspace_root = workspace_root.resolve()
        self.playwright_project_dir = (self.workspace_root / "playwright_scripts").resolve()
        self.reports_root = (self.workspace_root / "playwright_reports").resolve()
        self.results_root = (self.workspace_root / "playwright_results").resolve()

        if not self.playwright_project_dir.exists():
            raise FileNotFoundError(f"playwright_scripts not found: {self.playwright_project_dir}")

        self.tests_dir = (self.playwright_project_dir / "tests").resolve()
        self.run_configs_dir = (self.playwright_project_dir / ".run_configs").resolve()
        self.tests_dir.mkdir(parents=True, exist_ok=True)
        self.run_configs_dir.mkdir(parents=True, exist_ok=True)
        self.reports_root.mkdir(parents=True, exist_ok=True)
        self.results_root.mkdir(parents=True, exist_ok=True)

    def prepare_run(self, *, script_content: str, script_name: str = "", language: str = "typescript") -> PlaywrightRunLayout:
        ext = ".spec.ts" if (language or "").lower() != "javascript" else ".spec.js"

        run_id = generate_run_id()
        run_dir = self.reports_root / f"report_{run_id}"
        report_dir = run_dir / "report"
        artifacts_dir = run_dir / "artifacts"
        result_json = run_dir / f"result_{run_id}.json"

        run_dir.mkdir(parents=True, exist_ok=True)
        report_dir.mkdir(parents=True, exist_ok=True)
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        base = sanitize_basename(script_name)
        if base.endswith(".spec.ts"):
            base = base[: -len(".spec.ts")]
        elif base.endswith(".spec.js"):
            base = base[: -len(".spec.js")]
        if not base:
            base = "test"

        filename = f"{base}_{run_id}{ext}"
        script_in_run = run_dir / filename
        script_in_tests = self.tests_dir / filename
        script_in_run.write_text(script_content or "", encoding="utf-8")
        script_in_tests.write_text(script_content or "", encoding="utf-8")

        run_config_path = self._write_run_config(
            report_dir=report_dir,
            artifacts_dir=artifacts_dir,
            json_output_file=result_json,
        )

        return PlaywrightRunLayout(
            run_id=run_id,
            run_dir=run_dir,
            report_dir=report_dir,
            artifacts_dir=artifacts_dir,
            result_json=result_json,
            script_in_run=script_in_run,
            script_in_tests=script_in_tests,
            run_config_path=run_config_path,
        )

    def run(
        self,
        *,
        layout: PlaywrightRunLayout,
        browser: str = "chromium",
        headless: Optional[bool] = None,
        reporter: str = "html,json",
        env_vars: Optional[dict[str, str]] = None,
        timeout_seconds: Optional[int] = None,
    ) -> dict[str, Any]:
        playwright_binary = os.getenv("PLAYWRIGHT_BINARY", "npx")
        if platform.system() == "Windows" and playwright_binary == "npx":
            playwright_binary = "npx.cmd"

        cmd: list[str] = [playwright_binary, "playwright", "test", "-c", str(layout.run_config_path)]
        if browser:
            cmd.extend(["--project", browser])

        is_headless = True if headless is None else bool(headless)
        if not is_headless:
            cmd.append("--headed")

        # Run a single file.
        relative_script = layout.script_in_tests.relative_to(self.playwright_project_dir).as_posix()
        cmd.extend(["--", relative_script])

        env = os.environ.copy()
        if env_vars:
            for k, v in env_vars.items():
                if v is None:
                    continue
                env[str(k)] = str(v)

        result = subprocess.run(
            cmd,
            cwd=str(self.playwright_project_dir),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=env,
            timeout=timeout_seconds,
        )

        # Keep a stable entrypoint at run_dir/index.html for convenience.
        index_html = layout.report_dir / "index.html"
        html_report_ok = index_html.exists()
        root_index = layout.run_dir / "index.html"
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

        summary = None
        if layout.result_json.exists():
            try:
                summary = self._extract_summary(json.loads(layout.result_json.read_text(encoding="utf-8")))
            except Exception:
                summary = None

        # Copy result json into the legacy global results dir for backward compatibility.
        global_result = self.results_root / f"result_{layout.run_id}.json"
        if layout.result_json.exists():
            try:
                global_result.write_bytes(layout.result_json.read_bytes())
            except Exception:
                pass

        return {
            "success": result.returncode == 0,
            "run_id": layout.run_id,
            "run_dir": str(layout.run_dir),
            "script_in_tests": str(layout.script_in_tests),
            "browser": browser,
            "headless": is_headless,
            "reporter_requested": reporter,
            "command": " ".join(cmd),
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "json_result_run": str(layout.result_json) if layout.result_json.exists() else None,
            "json_result_global": str(global_result) if global_result.exists() else None,
            "html_report_dir": str(layout.report_dir),
            "html_report_index": str(index_html) if html_report_ok else None,
            "html_report_root_index": str(root_index) if html_report_ok else None,
            "artifacts_dir": str(layout.artifacts_dir),
            "summary": summary,
        }

    def parse_results(self, result_json_path: Path) -> dict[str, Any]:
        if not result_json_path.exists():
            return {"success": False, "error": f"result json not found: {result_json_path}"}
        try:
            raw = json.loads(result_json_path.read_text(encoding="utf-8"))
            return {
                "success": True,
                "summary": self._extract_summary(raw),
                "test_cases": self._extract_test_cases(raw),
                "errors": self._extract_errors(raw),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def zip_report_dir(self, report_dir: Path) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for path in report_dir.rglob("*"):
                if path.is_dir():
                    continue
                zf.write(path, arcname=str(path.relative_to(report_dir)).replace("\\", "/"))
        return buf.getvalue()

    def _write_run_config(self, *, report_dir: Path, artifacts_dir: Path, json_output_file: Path) -> Path:
        config_dir = self.run_configs_dir
        config_dir.mkdir(parents=True, exist_ok=True)

        config_path = config_dir / f"{report_dir.parent.name}.config.cjs"

        report_dir_posix = to_posix_path(report_dir)
        artifacts_dir_posix = to_posix_path(artifacts_dir)
        json_output_posix = to_posix_path(json_output_file)

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

    def _extract_summary(self, results: dict[str, Any]) -> dict[str, Any]:
        summary = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "flaky": 0,
            "duration_ms": 0,
        }
        if "stats" in results:
            stats = results["stats"] or {}
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

    def _extract_test_cases(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        test_cases: list[dict[str, Any]] = []
        for suite in results.get("suites", []) or []:
            self._collect_test_cases(suite, test_cases, [])
        return test_cases

    def _collect_test_cases(self, suite: dict[str, Any], test_cases: list[dict[str, Any]], parent_titles: list[str]) -> None:
        current_titles = parent_titles + [suite.get("title", "")]
        for spec in suite.get("specs", []) or []:
            file_path = spec.get("file", "")
            line = spec.get("line", 0)
            column = spec.get("column", 0)
            for test in spec.get("tests", []) or []:
                test_title = test.get("title", "")
                full_title = " > ".join([t for t in (current_titles + [test_title]) if t])
                for res in test.get("results", []) or []:
                    test_cases.append(
                        {
                            "title": test_title,
                            "full_title": full_title,
                            "file": file_path,
                            "line": line,
                            "column": column,
                            "status": res.get("status", "unknown"),
                            "duration_ms": res.get("duration", 0),
                            "retry": res.get("retry", 0),
                            "error": (res.get("error") or {}).get("message") if res.get("error") else None,
                            "attachments": len(res.get("attachments", []) or []),
                        }
                    )
        for sub_suite in suite.get("suites", []) or []:
            self._collect_test_cases(sub_suite, test_cases, current_titles)

    def _extract_errors(self, results: dict[str, Any]) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        for suite in results.get("suites", []) or []:
            self._collect_errors(suite, errors)
        return errors

    def _collect_errors(self, suite: dict[str, Any], errors: list[dict[str, Any]]) -> None:
        for spec in suite.get("specs", []) or []:
            for test in spec.get("tests", []) or []:
                for res in test.get("results", []) or []:
                    if res.get("status") in {"failed", "timedOut"}:
                        err = res.get("error") or {}
                        errors.append(
                            {
                                "test": test.get("title", ""),
                                "file": spec.get("file", ""),
                                "status": res.get("status", ""),
                                "error_message": err.get("message", ""),
                                "error_stack": err.get("stack", ""),
                            }
                        )
        for sub_suite in suite.get("suites", []) or []:
            self._collect_errors(sub_suite, errors)

