"""
UI Java Agent 工具模块

提供测试用例生成、页面变更检测、工作区管理等功能

工具使用方式:
1. Python 直接调用: 从此模块导入类和函数
2. LangChain Agent 调用: 使用 langchain_tools 模块中注册的 @tool 函数
"""

from .testcase_tools import (
    TestCase,
    TestStep,
    Priority,
    TestType,
    TestCaseGenerator,
    parse_test_plan,
    generate_test_cases,
)

from .excel_exporter import (
    ExcelExporter,
    export_ui_test_cases,
    export_all_test_cases,
)

from .page_change_detector import (
    PageChangeDetector,
    PageObjectParser,
    PlaywrightMCPElementParser,
    PageElement,
    LocatorMethod,
    LocatorChange,
    ChangeType,
    ConfidenceLevel,
    detect_page_changes,
)

from .workspace_manager import (
    WorkspaceManager,
    create_session_workspace as create_workspace_path,
    get_workspace_path,
)

# LangChain 工具（供 Agent 调用）
from .langchain_tools import (
    get_all_tools,
    init_workspace_manager,
)

__all__ = [
    # 测试用例
    "TestCase",
    "TestStep", 
    "Priority",
    "TestType",
    "TestCaseGenerator",
    "parse_test_plan",
    "generate_test_cases",
    # Excel 导出
    "ExcelExporter",
    "export_ui_test_cases",
    "export_all_test_cases",
    # 页面变更检测
    "PageChangeDetector",
    "PageObjectParser",
    "PlaywrightMCPElementParser",
    "PageElement",
    "LocatorMethod",
    "LocatorChange",
    "ChangeType",
    "ConfidenceLevel",
    "detect_page_changes",
    # 工作区管理
    "WorkspaceManager",
    "create_workspace_path",
    "get_workspace_path",
    # LangChain 工具
    "get_all_tools",
    "init_workspace_manager",
]
