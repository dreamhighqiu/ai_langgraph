"""Playwright test script generator + saver.

This tool saves the generated script into a run-scoped folder under
`playwright_reports/report_<run_id>` and also copies it into the executable
Playwright `tests` directory (`playwright_scripts/tests`) so it can be executed.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.tools import BaseTool, StructuredTool

from ui_automation.config import DEFAULT_CONFIG, UIAutomationConfig
from ui_automation.run_storage import (
    build_run_layout,
    generate_run_id,
    set_current_run_id,
    join_virtual,
    resolve_virtual_path,
    sanitize_basename,
)


def create_script_save_tool(config: UIAutomationConfig | None = None) -> BaseTool:
    cfg = config or DEFAULT_CONFIG

    def save_playwright_script(
        script_content: str,
        script_name: str = "",
        language: Literal["typescript", "javascript"] = "typescript",
    ) -> str:
        ext = ".spec.ts" if language == "typescript" else ".spec.js"

        run_id = generate_run_id()
        set_current_run_id(cfg, run_id)
        layout = build_run_layout(cfg, run_id)
        layout.run_dir_actual.mkdir(parents=True, exist_ok=True)
        layout.report_dir_actual.mkdir(parents=True, exist_ok=True)
        layout.artifacts_dir_actual.mkdir(parents=True, exist_ok=True)

        base = sanitize_basename(script_name)
        if base.endswith(".spec.ts"):
            base = base[: -len(".spec.ts")]
        elif base.endswith(".spec.js"):
            base = base[: -len(".spec.js")]
        if not base:
            base = "test"

        filename = f"{base}_{run_id}{ext}"

        run_script_virtual = join_virtual(layout.run_dir_virtual, filename)
        run_script_actual = resolve_virtual_path(run_script_virtual, cfg.workspace_root)
        run_script_actual.write_text(script_content, encoding="utf-8")

        executable_virtual = join_virtual(cfg.scripts_dir, filename)
        executable_actual = resolve_virtual_path(executable_virtual, cfg.workspace_root)
        executable_actual.parent.mkdir(parents=True, exist_ok=True)
        executable_actual.write_text(script_content, encoding="utf-8")

        return (
            "✅ Playwright脚本已保存（按单次对话/run隔离）\n"
            f"run_id: {run_id}\n"
            f"run_dir: {layout.run_dir_virtual}\n"
            f"script: {run_script_virtual}\n"
            f"executable_copy: {executable_virtual}\n"
            f"script_actual: {run_script_actual}\n"
            f"executable_actual: {executable_actual}"
        )

    return StructuredTool.from_function(
        name="save_playwright_script",
        func=save_playwright_script,
        description=(
            "保存 Playwright 测试脚本到单次对话(run)目录，并 copy 到 Playwright 可执行的 tests 目录。\n"
            "参数:\n"
            "- script_content: 脚本内容（必填）\n"
            "- script_name: 脚本名（可选）\n"
            "- language: 'typescript' 或 'javascript'（默认 typescript）\n"
            "返回: run_id、run_dir、脚本保存路径、可执行 copy 路径。"
        ),
    )
