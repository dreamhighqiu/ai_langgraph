from __future__ import annotations

from typing import Literal

from langchain_core.tools import BaseTool, StructuredTool

from ui_agent.automation.runtime_config import get_runtime_config
from ui_agent.automation.run_storage import (
    build_run_layout,
    generate_run_id,
    set_current_run_id,
    join_virtual,
    resolve_virtual_path,
    sanitize_basename,
)


def create_script_save_tool() -> BaseTool:
    cfg = get_runtime_config()

    def save_playwright_script(
        script_content: str,
        script_name: str = "",
        language: Literal["typescript", "javascript"] = "typescript",
    ) -> str:
        ext = ".spec.ts" if language == "typescript" else ".spec.js"

        run_id = generate_run_id()
        set_current_run_id(cfg.workspace_root, run_id)
        layout = build_run_layout(cfg.reports_dir, cfg.workspace_root, run_id)
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
            "Playwright script saved.\n"
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
            "Save Playwright script into run directory and executable tests folder.\n"
            "Args:\n"
            "- script_content: required\n"
            "- script_name: optional\n"
            "- language: typescript or javascript\n"
            "Returns run_id, run_dir, and script paths."
        ),
    )


def create_java_suite_save_tool() -> BaseTool:
    cfg = get_runtime_config()

    def save_playwright_java(
        java_code: str,
        class_name: str = "GeneratedTest",
        package_name: str = "",
    ) -> str:
        run_id = generate_run_id()
        set_current_run_id(cfg.workspace_root, run_id)
        layout = build_run_layout(cfg.reports_dir, cfg.workspace_root, run_id)
        layout.run_dir_actual.mkdir(parents=True, exist_ok=True)

        safe_class = sanitize_basename(class_name) or "GeneratedTest"
        filename = f"{safe_class}.java"

        run_java_virtual = join_virtual(layout.run_dir_virtual, filename)
        run_java_actual = resolve_virtual_path(run_java_virtual, cfg.workspace_root)
        run_java_actual.parent.mkdir(parents=True, exist_ok=True)

        content = java_code
        if package_name and not java_code.strip().startswith("package"):
            content = f"package {package_name};\n\n{java_code}"

        run_java_actual.write_text(content, encoding="utf-8")

        java_virtual = join_virtual(cfg.java_suites_dir, filename)
        java_actual = resolve_virtual_path(java_virtual, cfg.workspace_root)
        java_actual.parent.mkdir(parents=True, exist_ok=True)
        java_actual.write_text(content, encoding="utf-8")

        return (
            "Playwright Java suite saved.\n"
            f"run_id: {run_id}\n"
            f"run_dir: {layout.run_dir_virtual}\n"
            f"java: {run_java_virtual}\n"
            f"java_copy: {java_virtual}\n"
            f"java_actual: {run_java_actual}\n"
            f"java_copy_actual: {java_actual}"
        )

    return StructuredTool.from_function(
        name="save_playwright_java",
        func=save_playwright_java,
        description=(
            "Save Playwright Java test code into run directory and java suites folder.\n"
            "Args:\n"
            "- java_code: required\n"
            "- class_name: optional\n"
            "- package_name: optional\n"
            "Returns run_id and file paths."
        ),
    )
