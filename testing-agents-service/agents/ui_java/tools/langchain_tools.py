"""
LangChain 工具注册模块

将 Python 工具函数注册为 LangChain 工具，使 Agent 可以调用它们。

支持多对话隔离：每个 thread_id 拥有独立的工作区状态。
使用 InjectedToolArg 从 RunnableConfig 中自动获取 thread_id。
"""

import json
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Annotated
from langchain_core.tools import tool, InjectedToolArg
from langchain_core.runnables import RunnableConfig

from .workspace_manager import WorkspaceManager
from .page_change_detector import (
    PageChangeDetector,
    PageObjectParser,
    PlaywrightMCPElementParser,
    detect_page_changes,
)
from .excel_exporter import ExcelExporter


# ==================== 多对话隔离的工作区管理 ====================

class ThreadSafeWorkspaceRegistry:
    """
    线程安全的工作区注册表
    
    每个 thread_id 拥有独立的 WorkspaceManager 实例，
    确保多个对话同时运行时不会相互干扰。
    """
    
    def __init__(self, base_root: Path):
        self.base_root = base_root
        self._lock = threading.RLock()
        # thread_id -> WorkspaceManager
        self._managers: Dict[str, WorkspaceManager] = {}
        # thread_id -> 会话创建标记
        self._session_created: Dict[str, bool] = {}
        # thread_id -> 当前 URL
        self._current_urls: Dict[str, str] = {}
        # 默认管理器（用于没有 thread_id 的情况）
        self._default_manager = WorkspaceManager(base_root)
    
    def get_manager(self, thread_id: Optional[str] = None) -> WorkspaceManager:
        """获取指定对话的工作区管理器"""
        if not thread_id:
            return self._default_manager
        
        with self._lock:
            if thread_id not in self._managers:
                self._managers[thread_id] = WorkspaceManager(self.base_root)
                self._session_created[thread_id] = False
                self._current_urls[thread_id] = ""
            return self._managers[thread_id]
    
    def is_session_created(self, thread_id: Optional[str] = None) -> bool:
        """检查指定对话是否已创建工作区"""
        if not thread_id:
            return getattr(self._default_manager, '_session_created', False)
        
        with self._lock:
            return self._session_created.get(thread_id, False)
    
    def set_session_created(self, thread_id: Optional[str], created: bool):
        """设置指定对话的工作区创建状态"""
        if not thread_id:
            self._default_manager._session_created = created
            return
        
        with self._lock:
            self._session_created[thread_id] = created
    
    def get_current_url(self, thread_id: Optional[str] = None) -> str:
        """获取指定对话的当前 URL"""
        if not thread_id:
            return self._default_manager._current_url or ""
        
        with self._lock:
            return self._current_urls.get(thread_id, "")
    
    def set_current_url(self, thread_id: Optional[str], url: str):
        """设置指定对话的当前 URL"""
        if not thread_id:
            self._default_manager._current_url = url
            return
        
        with self._lock:
            self._current_urls[thread_id] = url
    
    def cleanup_thread(self, thread_id: str):
        """清理指定对话的资源（对话结束时调用）"""
        with self._lock:
            self._managers.pop(thread_id, None)
            self._session_created.pop(thread_id, None)
            self._current_urls.pop(thread_id, None)
    
    def get_active_threads(self) -> list:
        """获取所有活跃的对话 ID"""
        with self._lock:
            return list(self._managers.keys())


# 全局注册表实例
_workspace_registry: Optional[ThreadSafeWorkspaceRegistry] = None


def _get_thread_id(config: Optional[RunnableConfig]) -> Optional[str]:
    """从 RunnableConfig 中提取 thread_id"""
    if not config:
        return None
    configurable = config.get("configurable", {})
    return configurable.get("thread_id")


def init_workspace_manager(base_root: Path):
    """初始化工作区注册表"""
    global _workspace_registry
    _workspace_registry = ThreadSafeWorkspaceRegistry(base_root)
    return _workspace_registry


def get_workspace_manager() -> Optional[ThreadSafeWorkspaceRegistry]:
    """获取工作区注册表实例"""
    return _workspace_registry


def reset_session(thread_id: Optional[str] = None):
    """重置指定对话的会话状态"""
    if not _workspace_registry:
        return
    
    if thread_id:
        _workspace_registry.cleanup_thread(thread_id)


# ==================== 工作区管理工具 ====================

@tool(parse_docstring=True)
def create_session_workspace(
    url: str,
    config: Annotated[RunnableConfig, InjectedToolArg()]
) -> str:
    """
    根据 URL 创建或获取会话工作区目录。同一对话中相同URL会复用已有工作区，多个对话可同时运行互不干扰。
    
    Args:
        url: 目标页面 URL，如 https://chat.deepseek.com/dashboard
    
    Returns:
        工作区信息的 JSON 字符串，包含各子目录路径
    """
    global _workspace_registry
    
    if not _workspace_registry:
        return json.dumps({"error": "工作区管理器未初始化"}, ensure_ascii=False)
    
    try:
        thread_id = _get_thread_id(config)
        manager = _workspace_registry.get_manager(thread_id)
        
        # 检查是否已为当前 URL 创建过工作区
        current_url = _workspace_registry.get_current_url(thread_id)
        is_session_created = _workspace_registry.is_session_created(thread_id)
        
        if is_session_created and current_url == url and manager.current_workspace:
            # 已有工作区且 URL 相同，返回现有工作区
            result = {
                "success": True,
                "workspace": str(manager.current_workspace),
                "url": url,
                "page_name": manager.extract_page_name(url),
                "thread_id": thread_id,
                "directories": {
                    "pageobjects": str(manager.pageobjects_dir),
                    "testcases": str(manager.testcases_dir),
                    "reports": str(manager.reports_dir),
                    "excel": str(manager.excel_dir),
                    "helpers": str(manager.helpers_dir),
                },
                "message": f"使用现有工作区: {manager.current_workspace.name}",
                "is_existing": True
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # 创建新工作区
        workspace_path = manager.create_workspace(url)
        _workspace_registry.set_current_url(thread_id, url)
        _workspace_registry.set_session_created(thread_id, True)
        
        result = {
            "success": True,
            "workspace": str(workspace_path),
            "url": url,
            "page_name": manager.extract_page_name(url),
            "thread_id": thread_id,
            "directories": {
                "pageobjects": str(manager.pageobjects_dir),
                "testcases": str(manager.testcases_dir),
                "reports": str(manager.reports_dir),
                "excel": str(manager.excel_dir),
                "helpers": str(manager.helpers_dir),
            },
            "message": f"工作区创建成功: {workspace_path.name}",
            "is_existing": False
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool
def get_current_workspace(
    config: Annotated[RunnableConfig, InjectedToolArg()]
) -> str:
    """获取当前工作区信息，返回当前工作区的路径和子目录信息。"""
    global _workspace_registry
    
    if not _workspace_registry:
        return json.dumps({"error": "工作区管理器未初始化"}, ensure_ascii=False)
    
    thread_id = _get_thread_id(config)
    manager = _workspace_registry.get_manager(thread_id)
    
    if not manager.current_workspace:
        return json.dumps({
            "message": "尚未创建工作区，请先调用 create_session_workspace",
            "has_workspace": False,
            "thread_id": thread_id
        }, ensure_ascii=False)
    
    result = {
        "has_workspace": True,
        "workspace": str(manager.current_workspace),
        "workspace_name": manager.current_workspace.name,
        "url": _workspace_registry.get_current_url(thread_id),
        "thread_id": thread_id,
        "directories": {
            "pageobjects": str(manager.pageobjects_dir),
            "testcases": str(manager.testcases_dir),
            "reports": str(manager.reports_dir),
            "excel": str(manager.excel_dir),
            "helpers": str(manager.helpers_dir),
        }
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


@tool(parse_docstring=True)
def save_file_to_workspace(
    filename: str,
    content: str, 
    subdir: str = "",
    config: Annotated[RunnableConfig, InjectedToolArg()] = None
) -> str:
    """
    保存文件到当前工作区。必须提供文件名和内容两个参数。
    
    Args:
        filename: 必填！文件名（含扩展名），例如: LoginPage.java, TestPlan.md, TestCase.java
        content: 必填！文件的完整内容
        subdir: 子目录名，可选值: pageobjects（Java类）, testcases（测试代码）, reports（报告）, excel, helpers
    
    Returns:
        保存结果，包含文件完整路径
    """
    global _workspace_registry
    
    if not _workspace_registry:
        return json.dumps({
            "error": "工作区管理器未初始化",
            "suggestion": "请先调用 create_session_workspace 创建工作区"
        }, ensure_ascii=False)
    
    thread_id = _get_thread_id(config)
    manager = _workspace_registry.get_manager(thread_id)
    
    if not manager.current_workspace:
        return json.dumps({
            "error": "当前没有活动工作区",
            "suggestion": "请先调用 create_session_workspace 创建工作区",
            "thread_id": thread_id
        }, ensure_ascii=False)
    
    try:
        # 确定保存路径
        if subdir == "pageobjects":
            save_dir = manager.pageobjects_dir
        elif subdir == "testcases":
            save_dir = manager.testcases_dir
        elif subdir == "reports":
            save_dir = manager.reports_dir
        elif subdir == "excel":
            save_dir = manager.excel_dir
        elif subdir == "helpers":
            save_dir = manager.helpers_dir
        else:
            save_dir = manager.current_workspace
        
        # 确保目录存在
        save_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = save_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        return json.dumps({
            "success": True,
            "path": str(file_path),
            "workspace": str(manager.current_workspace),
            "subdir": subdir or "root",
            "thread_id": thread_id,
            "message": f"文件已保存: {file_path.name}"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# ==================== 页面变更检测工具 ====================

@tool(parse_docstring=True)
def detect_locator_changes(
    old_page_code: str, 
    snapshot_elements: str, 
    url: str = "",
    config: Annotated[RunnableConfig, InjectedToolArg()] = None
) -> str:
    """
    检测页面定位器变更，对比旧 PageObject 代码与当前页面元素，生成变更报告和新的 PageObject 类。
    
    Args:
        old_page_code: 旧的 PageObject Java 代码
        snapshot_elements: browser_snapshot 返回的页面元素数据
        url: 页面 URL，可选，用于报告
    
    Returns:
        检测结果 JSON，包含 summary、changes、new_page_code、html_report_path 等字段
    """
    global _workspace_registry
    
    try:
        thread_id = _get_thread_id(config)
        manager = _workspace_registry.get_manager(thread_id) if _workspace_registry else None
        
        # 使用 URL
        target_url = url or (_workspace_registry.get_current_url(thread_id) if _workspace_registry else "") or ""
        
        # 调用检测函数
        result = detect_page_changes(
            old_page_code=old_page_code,
            snapshot_data=snapshot_elements,
            url=target_url,
            workspace_path=manager.current_workspace if manager else None
        )
        
        # 保存报告到工作区
        html_report_path = None
        new_page_path = None
        
        if manager and manager.current_workspace:
            # 保存 HTML 报告
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_filename = f"ChangeReport_{timestamp}.html"
            report_path = manager.reports_dir / report_filename
            report_path.write_text(result['html_report'], encoding='utf-8')
            html_report_path = str(report_path)
            
            # 保存新的 PageObject
            page_filename = f"{result['class_name']}.java"
            page_path = manager.pageobjects_dir / page_filename
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
            "thread_id": thread_id,
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


@tool(parse_docstring=True) 
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

@tool(parse_docstring=True)
def save_test_cases_data(
    test_cases: str,
    module_name: str = "TestModule",
    config: Annotated[RunnableConfig, InjectedToolArg()] = None
) -> str:
    """
    保存 AI 生成的测试用例数据。AI 应该先理解测试计划，然后构造测试用例 JSON 数据传入此工具。
    
    Args:
        test_cases: AI 构造的测试用例 JSON 数组，每个用例包含 id, module, title, priority, type, steps_detail, expected_result 等字段
        module_name: 模块名称
    
    Returns:
        保存结果
    
    测试用例 JSON 格式示例:
    [
        {
            "id": "TC_BAIDU_001",
            "module": "百度首页",
            "title": "基本搜索功能",
            "priority": "P0",
            "type": "functional",
            "steps_detail": [
                {"order": 1, "action": "打开百度首页", "expected": "页面加载成功", "locator": ""},
                {"order": 2, "action": "在搜索框输入关键词", "expected": "关键词显示在搜索框", "locator": "#kw"},
                {"order": 3, "action": "点击搜索按钮", "expected": "跳转到结果页", "locator": "#su"}
            ],
            "expected_result": "显示搜索结果",
            "tags": ["smoke", "functional"],
            "test_data": {"keyword": "测试自动化"}
        }
    ]
    """
    global _workspace_registry
    
    try:
        thread_id = _get_thread_id(config)
        cases_list = json.loads(test_cases)
        
        if not isinstance(cases_list, list):
            cases_list = [cases_list]
        
        # 获取 URL
        target_url = ""
        if _workspace_registry:
            target_url = _workspace_registry.get_current_url(thread_id) or ""
        
        # 统计
        summary = {
            "total": len(cases_list),
            "by_priority": {},
            "by_type": {}
        }
        
        for tc in cases_list:
            priority = tc.get("priority", "P1")
            tc_type = tc.get("type", "functional")
            summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
            summary["by_type"][tc_type] = summary["by_type"].get(tc_type, 0) + 1
        
        result = {
            "success": True,
            "module_name": module_name,
            "url": target_url,
            "total_cases": len(cases_list),
            "thread_id": thread_id,
            "summary": summary,
            "test_cases": cases_list,
            "message": f"已保存 {len(cases_list)} 个测试用例"
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"JSON 解析错误: {str(e)}",
            "suggestion": "请确保传入有效的测试用例 JSON 数组"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


@tool(parse_docstring=True)
def export_testcases_to_excel(
    testcases_json: str, 
    filename: str = "", 
    module_name: str = "TestCases",
    config: Annotated[RunnableConfig, InjectedToolArg()] = None
) -> str:
    """
    将测试用例导出为 Excel 文件。
    
    Args:
        testcases_json: 测试用例 JSON 数据（来自 generate_test_cases_from_plan 的输出）
        filename: 输出文件名（可选，默认自动生成带时间戳的文件名）
        module_name: 模块名称，用于文件命名
    
    Returns:
        导出结果，包含文件路径
    """
    global _workspace_registry
    
    try:
        data = json.loads(testcases_json)
        thread_id = _get_thread_id(config)
        manager = _workspace_registry.get_manager(thread_id) if _workspace_registry else None
        
        # 支持两种格式：直接的用例列表，或包含 test_cases 字段的对象
        if isinstance(data, list):
            testcases = data
        elif isinstance(data, dict) and "test_cases" in data:
            testcases = data["test_cases"]
            # 使用数据中的模块名称（如果有）
            if "module_name" in data:
                module_name = data["module_name"]
        else:
            testcases = []
        
        if not testcases:
            return json.dumps({
                "error": "没有可导出的测试用例",
                "suggestion": "请先调用 generate_test_cases_from_plan 生成测试用例"
            }, ensure_ascii=False)
        
        # 生成文件名（如果未提供）
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{module_name}_TestCases_{timestamp}.xlsx"
        
        # 确保文件名以 .xlsx 结尾
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        # 确定保存路径
        if manager and manager.excel_dir:
            output_path = manager.excel_dir / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 如果没有工作区，保存到基础目录
            output_path = Path(filename)
        
        # 导出 Excel
        exporter = ExcelExporter()
        exporter.export(testcases, str(output_path))
        
        return json.dumps({
            "success": True,
            "path": str(output_path),
            "filename": filename,
            "cases_count": len(testcases),
            "thread_id": thread_id,
            "message": f"Excel 文件已导出: {output_path}"
        }, ensure_ascii=False)
        
    except json.JSONDecodeError as e:
        return json.dumps({
            "error": f"JSON 解析错误: {str(e)}",
            "suggestion": "请确保传入有效的测试用例 JSON 数据"
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
        # 测试用例导出（AI 构造数据，工具负责导出）
        save_test_cases_data,
        export_testcases_to_excel,
    ]
