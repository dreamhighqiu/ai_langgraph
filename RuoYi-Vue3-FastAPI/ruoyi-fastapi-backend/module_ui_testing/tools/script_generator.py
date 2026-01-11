"""Playwright测试脚本生成和保存工具.

此工具用于保存生成的Playwright测试脚本到数据库，并与module_testing集成。
"""

from __future__ import annotations

import asyncio
from typing import Literal

from langchain_core.tools import BaseTool, StructuredTool

from module_ui_testing.config import DEFAULT_CONFIG, UIAutomationConfig


def create_script_save_tool(config: UIAutomationConfig | None = None) -> BaseTool:
    """创建脚本保存工具."""
    cfg = config or DEFAULT_CONFIG

    def save_playwright_script(
        script_content: str,
        script_name: str = "",
        language: Literal["typescript", "javascript"] = "typescript",
        project_id: int = 0,
        description: str = "",
    ) -> str:
        """保存Playwright测试脚本.

        Args:
            script_content: 脚本内容
            script_name: 脚本名称
            language: 脚本语言（typescript或javascript）
            project_id: 项目ID
            description: 脚本描述

        Returns:
            保存结果信息
        """
        # 这个工具主要用于Agent生成脚本时调用
        # 实际保存到数据库的逻辑在Service层实现
        # 这里返回一个标识，让Agent知道脚本已生成
        
        ext = ".spec.ts" if language == "typescript" else ".spec.js"
        
        # 返回脚本信息，后续由Service层处理保存
        return f"""✅ Playwright测试脚本已生成

脚本信息：
- 脚本名称：{script_name or "test"}{ext}
- 脚本语言：{language}
- 项目ID：{project_id}
- 脚本长度：{len(script_content)} 字符
- 描述：{description or "无"}

脚本内容：
```{language}
{script_content}
```

请使用此脚本内容调用API保存到数据库。
"""

    return StructuredTool.from_function(
        name="save_playwright_script",
        func=save_playwright_script,
        description=(
            "生成并保存Playwright测试脚本。\n"
            "参数:\n"
            "- script_content: 脚本内容（必填）\n"
            "- script_name: 脚本名称（可选）\n"
            "- language: 'typescript' 或 'javascript'（默认 typescript）\n"
            "- project_id: 项目ID（必填）\n"
            "- description: 脚本描述（可选）\n"
            "返回: 脚本生成信息"
        ),
    )

