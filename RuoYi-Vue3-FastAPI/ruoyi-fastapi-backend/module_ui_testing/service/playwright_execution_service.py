"""
UI automation execution service for Playwright.

Wires PlaywrightRunner (real execution) into the platform execution/report tables:
- Updates `test_execution` status/result
- Creates `test_report` records (HTML summary + Playwright HTML report zip)
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from module_testing.dao.execution_dao import ExecutionDAO
from module_testing.entity.do.script_do import TestScript
from module_testing.service.report_service import ReportService
from module_ui_testing.service.playwright_runner import PlaywrightRunner
from utils.log_util import logger


class PlaywrightExecutionService:
    @staticmethod
    async def execute(
        *,
        db: AsyncSession,
        execution_id: int,
        script: TestScript,
        execution_config: Optional[dict] = None,
        executor: str = "",
    ) -> dict[str, Any]:
        cfg = execution_config or {}
        browser = cfg.get("browser") or "chromium"
        headless = cfg.get("headless")
        env_vars = cfg.get("env_vars") or {}
        timeout_ms = cfg.get("timeout") or cfg.get("timeout_ms")
        timeout_seconds = int(timeout_ms / 1000) if isinstance(timeout_ms, (int, float)) and timeout_ms > 0 else None

        start_time = datetime.now()
        await ExecutionDAO.update_status(
            db,
            execution_id,
            "running",
            start_time=start_time,
            agent_id="playwright_runner",
            executor=executor,
        )
        await db.commit()

        runner = PlaywrightRunner()
        layout = runner.prepare_run(script_content=script.script_content or "", script_name=script.script_name, language="typescript")

        try:
            # Run in a thread to avoid blocking the event loop.
            run_result = await asyncio.to_thread(
                runner.run,
                layout=layout,
                browser=browser,
                headless=headless,
                env_vars=env_vars,
                timeout_seconds=timeout_seconds,
            )
        except Exception as e:
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())
            await ExecutionDAO.update_status(
                db,
                execution_id,
                "failed",
                end_time=end_time,
                duration=duration,
                thread_id=layout.run_id,
                agent_id="playwright_runner",
                result={"error": str(e), "run_id": layout.run_id},
                error_msg=str(e),
            )
            await db.commit()
            return {"success": False, "execution_id": execution_id, "run_id": layout.run_id, "status": "failed", "error": str(e)}

        parsed = runner.parse_results(layout.result_json) if layout.result_json.exists() else {"success": False, "error": "no result json"}
        end_time = datetime.now()
        duration = int((end_time - start_time).total_seconds())

        result_payload: dict[str, Any] = {
            "run": run_result,
            "parsed": parsed,
        }

        status = "success" if run_result.get("success") else "failed"
        error_msg = None if run_result.get("success") else (run_result.get("stderr") or "Playwright execution failed")

        await ExecutionDAO.update_status(
            db,
            execution_id,
            status,
            end_time=end_time,
            duration=duration,
            thread_id=layout.run_id,
            agent_id="playwright_runner",
            result=result_payload,
            error_msg=error_msg,
        )
        await db.commit()

        # Reports: HTML summary (viewable) + Playwright HTML report zip (downloadable)
        created_reports: list[dict[str, Any]] = []
        try:
            summary_html = PlaywrightExecutionService._build_summary_html(
                script_name=script.script_name,
                execution_id=execution_id,
                run_id=layout.run_id,
                browser=browser,
                run_result=run_result,
                parsed=parsed,
            )
            r1 = await ReportService.create_report(
                db=db,
                execution_id=execution_id,
                report_name=f"Playwright Summary - {script.script_name} - {layout.run_id}",
                report_type="html",
                content=summary_html,
                summary=(parsed.get("summary") if isinstance(parsed, dict) else None),
                metrics={"browser": browser, "run_id": layout.run_id},
            )
            if r1.get("success"):
                created_reports.append({"report_id": r1.get("report_id"), "report_type": "html"})
        except Exception as e:
            logger.warning(f"Playwright summary report creation failed: {e}")

        try:
            if layout.report_dir.exists():
                zip_bytes = runner.zip_report_dir(layout.report_dir)
                r2 = await ReportService.create_report(
                    db=db,
                    execution_id=execution_id,
                    report_name=f"Playwright HTML Report (zip) - {script.script_name} - {layout.run_id}",
                    report_type="allure",
                    content=zip_bytes,
                    summary=(parsed.get("summary") if isinstance(parsed, dict) else None),
                    metrics={"browser": browser, "run_id": layout.run_id, "format": "playwright_html_zip"},
                )
                if r2.get("success"):
                    created_reports.append({"report_id": r2.get("report_id"), "report_type": "allure"})
        except Exception as e:
            logger.warning(f"Playwright HTML report zip creation failed: {e}")

        if created_reports:
            # Attach report ids back onto execution result payload for convenience.
            result_payload["reports"] = created_reports
            await ExecutionDAO.update_status(db, execution_id, status, result=result_payload)
            await db.commit()

        return {
            "success": run_result.get("success", False),
            "execution_id": execution_id,
            "run_id": layout.run_id,
            "status": status,
            "reports": created_reports,
        }

    @staticmethod
    def _build_summary_html(
        *,
        script_name: str,
        execution_id: int,
        run_id: str,
        browser: str,
        run_result: dict[str, Any],
        parsed: dict[str, Any],
    ) -> str:
        summary = parsed.get("summary") or {}
        errors = parsed.get("errors") or []
        ok = bool(run_result.get("success"))
        status_text = "PASSED" if ok else "FAILED"

        def esc(text: Any) -> str:
            s = "" if text is None else str(text)
            return (
                s.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;")
            )

        error_rows = ""
        for e in errors[:50]:
            error_rows += (
                "<tr>"
                f"<td>{esc(e.get('test'))}</td>"
                f"<td>{esc(e.get('file'))}</td>"
                f"<td>{esc(e.get('status'))}</td>"
                f"<td><pre style=\"white-space:pre-wrap;\">{esc(e.get('error_message'))}</pre></td>"
                "</tr>"
            )

        # 提取包含反斜杠的字符串到变量中，避免f-string表达式中包含反斜杠
        empty_row = '<tr><td colspan="4" class="muted">无</td></tr>'
        badge_color = '#16a34a' if ok else '#dc2626'
        
        return f"""\
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Playwright 测试报告 - {esc(script_name)}</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Microsoft YaHei', Arial, sans-serif; margin: 0; background: #f6f8fb; color: #1f2d3d; }}
    .container {{ max-width: 1200px; margin: 24px auto; padding: 0 16px; }}
    .card {{ background: #fff; border: 1px solid #e5e7eb; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    .title {{ display:flex; align-items: baseline; justify-content: space-between; gap: 12px; }}
    .badge {{ padding: 4px 10px; border-radius: 999px; font-weight: 600; font-size: 12px; color: #fff; background: {badge_color}; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, minmax(0, 1fr)); gap: 12px; }}
    .stat {{ background: #f9fafb; border: 1px solid #eef2f7; border-radius: 10px; padding: 12px; }}
    .stat .k {{ font-size: 12px; color: #64748b; }}
    .stat .v {{ font-size: 20px; font-weight: 700; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid #eef2f7; padding: 10px; text-align: left; vertical-align: top; }}
    th {{ background: #f9fafb; color: #334155; font-weight: 600; }}
    pre {{ margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace; font-size: 12px; }}
    .muted {{ color: #64748b; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="card">
      <div class="title">
        <div>
          <h2 style="margin:0;">Playwright 测试报告</h2>
          <div class="muted" style="margin-top:6px;">脚本：{esc(script_name)} | 执行ID：{execution_id} | Run：{esc(run_id)} | 浏览器：{esc(browser)}</div>
        </div>
        <div class="badge">{status_text}</div>
      </div>
    </div>

    <div class="card">
      <div class="grid">
        <div class="stat"><div class="k">Total</div><div class="v">{esc(summary.get('total', 0))}</div></div>
        <div class="stat"><div class="k">Passed</div><div class="v">{esc(summary.get('passed', 0))}</div></div>
        <div class="stat"><div class="k">Failed</div><div class="v">{esc(summary.get('failed', 0))}</div></div>
        <div class="stat"><div class="k">Skipped</div><div class="v">{esc(summary.get('skipped', 0))}</div></div>
        <div class="stat"><div class="k">Duration (ms)</div><div class="v">{esc(summary.get('duration_ms', 0))}</div></div>
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0 0 12px 0;">运行信息</h3>
      <div class="muted">HTML 报告目录：{esc(run_result.get('html_report_dir'))}</div>
      <div class="muted">JSON 结果：{esc(run_result.get('json_result_run'))}</div>
      <div style="margin-top:10px;">
        <details>
          <summary>命令与输出（stdout/stderr）</summary>
          <div style="margin-top:10px;" class="muted">Command: <pre>{esc(run_result.get('command'))}</pre></div>
          <div style="margin-top:10px;">
            <div class="muted">stdout</div>
            <pre style="white-space:pre-wrap;">{esc(run_result.get('stdout'))}</pre>
          </div>
          <div style="margin-top:10px;">
            <div class="muted">stderr</div>
            <pre style="white-space:pre-wrap;">{esc(run_result.get('stderr'))}</pre>
          </div>
        </details>
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0 0 12px 0;">失败用例（最多50条）</h3>
      <table>
        <thead><tr><th>Test</th><th>File</th><th>Status</th><th>Error</th></tr></thead>
        <tbody>{error_rows or empty_row}</tbody>
      </table>
    </div>
  </div>
</body>
</html>
"""
