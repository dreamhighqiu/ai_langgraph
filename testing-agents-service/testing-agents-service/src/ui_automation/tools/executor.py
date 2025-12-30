"""Playwright脚本执行工具."""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""


import json
import os
import platform
import subprocess
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any

from langchain_core.tools import StructuredTool, BaseTool

from ui_automation.config import UIAutomationConfig, DEFAULT_CONFIG

# pylint: disable  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZERGcVJRPT06MDUyMGE3M2M=

def _resolve_virtual_path(virtual_path: str, workspace_root: str) -> Path:
    """将虚拟路径解析为实际文件系统路径."""
    relative_path = virtual_path.lstrip("/")
    return Path(workspace_root).resolve() / relative_path


def _to_virtual_path(results_dir: str, result_name: str) -> str:
    """生成虚拟路径."""
    if not results_dir.startswith("/"):
        results_dir = "/" + results_dir
    results_dir = results_dir.rstrip("/")
    return f"{results_dir}/{result_name}"


def create_playwright_executor_tool(config: UIAutomationConfig | None = None) -> BaseTool:
    """创建Playwright脚本执行工具.

    Args:
        config: UI自动化配置

    Returns:
        Playwright执行工具
    """
    cfg = config or DEFAULT_CONFIG

    def run_playwright_script(
        script_path: str,
        browser: str = "",
        headless: bool | None = None,
        reporter: str = "html,json",
    ) -> str:
        """执行Playwright测试脚本.

        Args:
            script_path: Playwright脚本虚拟路径（以 / 开头，如 /playwright_scripts/tests/test.spec.ts）
            browser: 浏览器类型（chromium/firefox/webkit），默认使用配置中的浏览器
            headless: 是否无头模式，默认使用配置中的设置
            reporter: 报告格式（html/json/list/dot/line），可以组合使用，用逗号分隔

        Returns:
            测试结果（JSON格式）
        """
        # 将虚拟路径解析为实际路径
        actual_script_path = _resolve_virtual_path(script_path, cfg.workspace_root)

        if not actual_script_path.exists():
            return json.dumps({
                "success": False,
                "error": f"脚本文件不存在: {script_path}",
                "actual_path": str(actual_script_path),
            }, ensure_ascii=False, indent=2)

        # 确定 Playwright 项目的工作目录
        # 如果脚本在 playwright_scripts 目录下，使用该目录作为工作目录
        playwright_cwd = Path(cfg.workspace_root).resolve()
        if "playwright_scripts" in actual_script_path.parts:
            # 找到 playwright_scripts 目录
            for i, part in enumerate(actual_script_path.parts):
                if part == "playwright_scripts":
                    playwright_cwd = Path(*actual_script_path.parts[:i+1])
                    break

        # 确保结果目录存在
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_id = str(uuid.uuid4())[:8]
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZERGcVJRPT06MDUyMGE3M2M=
        
        # JSON结果文件
        json_result_name = f"result_{timestamp}_{result_id}.json"
        virtual_json_path = _to_virtual_path(cfg.results_dir, json_result_name)
        actual_json_path = _resolve_virtual_path(virtual_json_path, cfg.workspace_root)
        actual_json_path.parent.mkdir(parents=True, exist_ok=True)

        # HTML报告目录
        html_report_name = f"report_{timestamp}_{result_id}"
        virtual_html_path = _to_virtual_path(cfg.reports_dir, html_report_name)
        actual_html_path = _resolve_virtual_path(virtual_html_path, cfg.workspace_root)
        actual_html_path.mkdir(parents=True, exist_ok=True)

        # 构建Playwright命令
        # 在 Windows 上，如果使用 npx，需要使用 npx.cmd
        playwright_binary = cfg.playwright_binary
        if platform.system() == "Windows" and playwright_binary == "npx":
            playwright_binary = "npx.cmd"

        cmd = [playwright_binary] + cfg.playwright_args
        
        # 添加浏览器参数
        browser_type = browser or cfg.default_browser
        cmd.extend(["--project", browser_type])
        
        # 添加headless参数
        is_headless = headless if headless is not None else cfg.default_headless
        if not is_headless:
            cmd.append("--headed")
        
        # 准备环境变量用于 reporter 输出路径
        env = os.environ.copy()

        # 添加reporter参数
        # 对于 json 和 html reporter，使用环境变量设置输出路径
        reporters = reporter.split(",")
        for rep in reporters:
            rep = rep.strip()
            if rep == "html":
                # HTML reporter 使用 outputFolder 选项
                try:
                    relative_html_path = os.path.relpath(actual_html_path, playwright_cwd)
                    # 转换为正斜杠格式（Playwright 在 Windows 上也接受）
                    relative_html_path = relative_html_path.replace("\\", "/")
                    cmd.extend(["--reporter", f"html={relative_html_path}"])
                except ValueError:
                    # 如果无法计算相对路径，使用绝对路径并转换为正斜杠
                    abs_path = str(actual_html_path).replace("\\", "/")
                    cmd.extend(["--reporter", f"html={abs_path}"])
            elif rep == "json":
                # JSON reporter 使用环境变量设置输出文件
                try:
                    relative_json_path = os.path.relpath(actual_json_path, playwright_cwd)
                    # 转换为正斜杠格式
                    relative_json_path = relative_json_path.replace("\\", "/")
                    env["PLAYWRIGHT_JSON_OUTPUT_FILE"] = relative_json_path
                except ValueError:
                    # 如果无法计算相对路径，使用绝对路径
                    abs_path = str(actual_json_path).replace("\\", "/")
                    env["PLAYWRIGHT_JSON_OUTPUT_FILE"] = abs_path
                cmd.extend(["--reporter", "json"])
            else:
                cmd.extend(["--reporter", rep])
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZERGcVJRPT06MDUyMGE3M2M=

        # 添加脚本路径（相对于工作目录）
        try:
            relative_script_path = actual_script_path.relative_to(playwright_cwd)
            # 转换为正斜杠格式（Playwright 在 Windows 上也接受）
            script_path_str = str(relative_script_path).replace("\\", "/")
            cmd.append(script_path_str)
        except ValueError:
            # 如果无法计算相对路径，使用绝对路径并转换为正斜杠
            script_path_str = str(actual_script_path).replace("\\", "/")
            cmd.append(script_path_str)

        try:
            # 执行Playwright（使用 playwright_cwd 作为工作目录）
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',  # 在 Windows 上使用 UTF-8 编码
                errors='replace',  # 遇到无法解码的字符时替换
                timeout=600,  # 10分钟超时
                cwd=str(playwright_cwd),
                env=env,  # 传递环境变量（包含 PLAYWRIGHT_JSON_OUTPUT_FILE）
            )

            # 解析结果
            output = {
                "success": result.returncode == 0,
                "script_path": script_path,
                "browser": browser_type,
                "headless": is_headless,
                "json_result": virtual_json_path if actual_json_path.exists() else None,
                "html_report": virtual_html_path if actual_html_path.exists() else None,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
            }

            # 如果有JSON结果文件，读取并解析
            if actual_json_path.exists():
                try:
                    with open(actual_json_path, "r", encoding="utf-8") as f:
                        test_results = json.load(f)
                        output["summary"] = _extract_summary(test_results)
                except Exception as e:
                    output["parse_error"] = str(e)

            return json.dumps(output, ensure_ascii=False, indent=2)

        except subprocess.TimeoutExpired:
            return json.dumps({
                "success": False,
                "error": "Playwright执行超时（>10分钟）",
                "script_path": script_path,
            }, ensure_ascii=False, indent=2)
        except FileNotFoundError:
            return json.dumps({
                "success": False,
                "error": f"Playwright未安装或路径错误: {cfg.playwright_binary}",
                "script_path": script_path,
            }, ensure_ascii=False, indent=2)
        except Exception as e:
            return json.dumps({
                "success": False,
                "error": str(e),
                "script_path": script_path,
            }, ensure_ascii=False, indent=2)

    return StructuredTool.from_function(
        name="run_playwright_script",
        func=run_playwright_script,
        description="""执行Playwright测试脚本。
参数：
- script_path: 脚本虚拟路径（必需，如 /playwright_scripts/test.spec.ts）
- browser: 浏览器类型（可选，chromium/firefox/webkit，默认chromium）
- headless: 是否无头模式（可选，默认True）
- reporter: 报告格式（可选，默认 'html,json'，可选 html/json/list/dot/line）

返回JSON格式的测试结果，包括成功状态、结果文件路径、测试摘要等。""",
    )


def _extract_summary(test_results: dict[str, Any]) -> dict[str, Any]:
    """从Playwright JSON结果中提取摘要信息."""
    summary = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "skipped": 0,
        "duration": 0,
    }
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZERGcVJRPT06MDUyMGE3M2M=
    
    # Playwright JSON格式解析
    if "suites" in test_results:
        for suite in test_results.get("suites", []):
            _count_tests(suite, summary)
    
    if "stats" in test_results:
        stats = test_results["stats"]
        summary.update({
            "total": stats.get("expected", 0) + stats.get("unexpected", 0) + stats.get("skipped", 0),
            "passed": stats.get("expected", 0),
            "failed": stats.get("unexpected", 0),
            "skipped": stats.get("skipped", 0),
            "duration": stats.get("duration", 0),
        })
    
    return summary


def _count_tests(suite: dict, summary: dict) -> None:
    """递归统计测试用例."""
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
    
    # 递归处理子suite
    for sub_suite in suite.get("suites", []):
        _count_tests(sub_suite, summary)

