"""
LangChain 工具注册模块

将 Python 工具函数注册为 LangChain 工具，使 Agent 可以调用它们。
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from langchain_core.tools import tool

from .workspace_manager import WorkspaceManager
from .page_change_detector import (
    PageChangeDetector,
    PageObjectParser,
    PlaywrightMCPElementParser,
    detect_page_changes,
)
from .excel_exporter import ExcelExporter
from .testcase_tools import TestCaseGenerator, generate_test_cases


# 全局工作区管理器实例（会在 Agent 初始化时设置）
_workspace_manager: Optional[WorkspaceManager] = None
_current_url: Optional[str] = None


def init_workspace_manager(base_root: Path):
    """初始化工作区管理器"""
    global _workspace_manager
    _workspace_manager = WorkspaceManager(base_root)
    return _workspace_manager


def get_workspace_manager() -> Optional[WorkspaceManager]:
    """获取工作区管理器实例"""
    return _workspace_manager


# ==================== 工作区管理工具 ====================

@tool
def create_session_workspace(url: str) -> str:
    """
    根据 URL 创建会话工作区目录。
    
    工作区命名格式: {page_name}_{YYYYMMDD}_{HHMMSS}
    例如: dashboard_20260131_143025
    
    调用时机: 在开始处理新页面之前调用此工具
    
    Args:
        url: 目标页面 URL，如 https://chat.deepseek.com/dashboard
    
    Returns:
        工作区信息的 JSON 字符串，包含各子目录路径
    """
    global _workspace_manager, _current_url
    
    if not _workspace_manager:
        return json.dumps({"error": "工作区管理器未初始化"}, ensure_ascii=False)
    
    try:
        workspace_path = _workspace_manager.create_workspace(url)
        _current_url = url
        
        result = {
            "success": True,
            "workspace": str(workspace_path),
            "url": url,
            "page_name": _workspace_manager.extract_page_name(url),
            "directories": {
                "pageobjects": str(_workspace_manager.pageobjects_dir),
                "testcases": str(_workspace_manager.testcases_dir),
                "reports": str(_workspace_manager.reports_dir),
                "excel": str(_workspace_manager.excel_dir),
                "helpers": str(_workspace_manager.helpers_dir),
            },
            "message": f"工作区创建成功: {workspace_path.name}"
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def get_current_workspace() -> str:
    """
    获取当前工作区信息。
    
    Returns:
        当前工作区的路径和子目录信息
    """
    global _workspace_manager
    
    if not _workspace_manager:
        return json.dumps({"error": "工作区管理器未初始化"}, ensure_ascii=False)
    
    if not _workspace_manager.current_workspace:
        return json.dumps({"message": "尚未创建工作区，请先调用 create_session_workspace"}, ensure_ascii=False)
    
    result = {
        "workspace": str(_workspace_manager.current_workspace),
        "directories": {
            "pageobjects": str(_workspace_manager.pageobjects_dir),
            "testcases": str(_workspace_manager.testcases_dir),
            "reports": str(_workspace_manager.reports_dir),
            "excel": str(_workspace_manager.excel_dir),
            "helpers": str(_workspace_manager.helpers_dir),
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool
def save_file_to_workspace(content: str, filename: str, subdir: str = "") -> str:
    """
    保存文件到当前工作区。
    
    Args:
        content: 文件内容
        filename: 文件名（如 LoginPage.java）
        subdir: 子目录（可选: pageobjects, testcases, reports, excel, helpers）
    
    Returns:
        保存结果
    """
    global _workspace_manager
    
    if not _workspace_manager or not _workspace_manager.current_workspace:
        return json.dumps({"error": "请先调用 create_session_workspace 创建工作区"}, ensure_ascii=False)
    
    try:
        # 确定保存路径
        if subdir == "pageobjects":
            save_dir = _workspace_manager.pageobjects_dir
        elif subdir == "testcases":
            save_dir = _workspace_manager.testcases_dir
        elif subdir == "reports":
            save_dir = _workspace_manager.reports_dir
        elif subdir == "excel":
            save_dir = _workspace_manager.excel_dir
        elif subdir == "helpers":
            save_dir = _workspace_manager.helpers_dir
        else:
            save_dir = _workspace_manager.current_workspace
        
        file_path = save_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        return json.dumps({
            "success": True,
            "path": str(file_path),
            "message": f"文件已保存: {file_path}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== 页面变更检测工具 ====================

@tool
def detect_locator_changes(old_page_code: str, snapshot_elements: str, url: str = "") -> str:
    """
    检测页面定位器变更。
    
    对比旧的 PageObject Java 代码与当前页面元素（来自 browser_snapshot），
    检测定位器变化，生成变更报告和新的 PageObject 类。
    
    使用流程:
    1. 先调用 browser_navigate 打开目标页面
    2. 调用 browser_snapshot 获取页面元素
    3. 调用此工具进行对比
    
    Args:
        old_page_code: 旧的 PageObject Java 代码
        snapshot_elements: browser_snapshot 返回的页面元素数据
        url: 页面 URL（可选，用于报告）
    
    Returns:
        检测结果 JSON，包含:
        - summary: 变更统计
        - changes: 变更详情列表
        - new_page_code: 新生成的 PageObject 代码
        - html_report_path: HTML 报告保存路径（如果有工作区）
    """
    global _workspace_manager, _current_url
    
    try:
        # 使用 URL
        target_url = url or _current_url or ""
        
        # 调用检测函数
        result = detect_page_changes(
            old_page_code=old_page_code,
            snapshot_data=snapshot_elements,
            url=target_url,
            workspace_path=_workspace_manager.current_workspace if _workspace_manager else None
        )
        
        # 保存报告到工作区
        html_report_path = None
        new_page_path = None
        
        if _workspace_manager and _workspace_manager.current_workspace:
            # 保存 HTML 报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"ChangeReport_{timestamp}.html"
            report_path = _workspace_manager.reports_dir / report_filename
            report_path.write_text(result['html_report'], encoding='utf-8')
            html_report_path = str(report_path)
            
            # 保存新的 PageObject
            page_filename = f"{result['class_name']}.java"
            page_path = _workspace_manager.pageobjects_dir / page_filename
            page_path.write_text(result['new_page_code'], encoding='utf-8')
            new_page_path = str(page_path)
        
        # 构建变更详情（简化版，不包含完整代码）
        changes_summary = []
        for c in result['changes']:
            changes_summary.append({
                "method": c.method_name,
                "type": c.change_type.value,
                "confidence": f"{c.confidence:.0%}",
                "needs_review": c.needs_review,
                "old_locator": c.old_locator[:50] + "..." if c.old_locator and len(c.old_locator) > 50 else c.old_locator,
                "new_locator": c.new_locator[:50] + "..." if c.new_locator and len(c.new_locator) > 50 else c.new_locator,
                "reason": c.reason
            })
        
        output = {
            "success": True,
            "class_name": result['class_name'],
            "url": target_url,
            "summary": result['summary'],
            "changes": changes_summary,
            "files_saved": {
                "html_report": html_report_path,
                "new_page_object": new_page_path
            },
            "message": f"检测完成: {result['summary']['modified']} 修改, {result['summary']['added']} 新增, {result['summary']['deleted']} 删除"
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool  
def parse_page_object(java_code: str) -> str:
    """
    解析 Java PageObject 代码，提取所有定位器方法。
    
    Args:
        java_code: Java PageObject 源代码
    
    Returns:
        解析结果 JSON，包含类名和方法列表
    """
    try:
        class_name, methods = PageObjectParser.parse(java_code)
        
        method_list = []
        for m in methods:
            method_list.append({
                "name": m.name,
                "locator": m.locator,
                "return_type": m.return_type,
                "line_number": m.line_number
            })
        
        return json.dumps({
            "class_name": class_name,
            "method_count": len(methods),
            "methods": method_list
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== 测试用例生成工具 ====================

@tool
def generate_test_cases_from_plan(test_plan: str, output_type: str = "all") -> str:
    """
    根据测试计划生成测试用例。
    
    Args:
        test_plan: 测试计划文本（Markdown 格式）
        output_type: 输出类型 - "ui"(UI测试用例), "all"(全量测试用例), "both"(两者都生成)
    
    Returns:
        生成的测试用例 JSON
    """
    try:
        result = generate_test_cases(test_plan, output_type)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def export_testcases_to_excel(testcases_json: str, filename: str = "testcases.xlsx") -> str:
    """
    将测试用例导出为 Excel 文件。
    
    Args:
        testcases_json: 测试用例 JSON 数据
        filename: 输出文件名
    
    Returns:
        导出结果
    """
    global _workspace_manager
    
    try:
        testcases = json.loads(testcases_json)
        
        # 确定保存路径
        if _workspace_manager and _workspace_manager.excel_dir:
            output_path = _workspace_manager.excel_dir / filename
        else:
            output_path = Path(filename)
        
        # 导出 Excel
        exporter = ExcelExporter()
        exporter.export(testcases, str(output_path))
        
        return json.dumps({
            "success": True,
            "path": str(output_path),
            "message": f"Excel 文件已导出: {output_path}"
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== 获取所有工具 ====================

def get_all_tools():
    """获取所有注册的 LangChain 工具"""
    return [
        # 工作区管理
        create_session_workspace,
        get_current_workspace,
        save_file_to_workspace,
        # 页面变更检测
        detect_locator_changes,
        parse_page_object,
        # 测试用例生成
        generate_test_cases_from_plan,
        export_testcases_to_excel,
    ]

