"""Playwright脚本执行工具.

此工具用于执行Playwright测试脚本，但实际执行逻辑在Service层。
Agent主要用于生成脚本，执行由API触发。
"""

from __future__ import annotations

from langchain_core.tools import BaseTool, StructuredTool

from module_ui_testing.config import DEFAULT_CONFIG, UIAutomationConfig


def create_playwright_executor_tool(config: UIAutomationConfig | None = None) -> BaseTool:
    """创建Playwright执行工具."""
    cfg = config or DEFAULT_CONFIG

    def run_playwright_script(
        script_id: int,
        browser: str = "chromium",
        headless: bool = True,
    ) -> str:
        """执行Playwright测试脚本.

        Args:
            script_id: 脚本ID
            browser: 浏览器类型（chromium/firefox/webkit）
            headless: 是否无头模式

        Returns:
            执行信息
        """
        # Agent不直接执行脚本，而是返回执行建议
        # 实际执行由API触发
        
        return f"""📋 Playwright脚本执行请求

脚本ID：{script_id}
浏览器：{browser}
无头模式：{"是" if headless else "否"}

⚠️ 注意：实际执行需要通过API接口触发。
请告知用户使用以下API执行脚本：
POST /api/testing/script/execute
{{
    "script_id": {script_id},
    "execution_config": {{
        "browser": "{browser}",
        "headless": {str(headless).lower()}
    }}
}}
"""

    return StructuredTool.from_function(
        name="run_playwright_script",
        func=run_playwright_script,
        description=(
            "请求执行Playwright测试脚本。\n"
            "参数:\n"
            "- script_id: 脚本ID（必填）\n"
            "- browser: 浏览器类型（chromium/firefox/webkit，默认chromium）\n"
            "- headless: 是否无头模式（默认True）\n"
            "返回: 执行请求信息"
        ),
    )

