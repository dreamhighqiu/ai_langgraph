"""
场景检测器 - 识别 UI 交互场景和 API 测试场景
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ScenarioType(Enum):
    """场景类型"""
    # 基础场景
    PAGE_LOAD = "page_load"
    NAVIGATION = "navigation"
    BUTTON_CLICK = "button_click"
    
    # 表单场景
    FORM_SUBMIT = "form_submit"
    FORM_VALIDATION = "form_validation"
    MULTI_STEP_FORM = "multi_step_form"
    
    # 交互组件
    MODAL_DIALOG = "modal_dialog"
    DROPDOWN_SELECT = "dropdown_select"
    TAB_NAVIGATION = "tab_navigation"
    ACCORDION = "accordion"
    TOOLTIP = "tooltip"
    
    # 数据展示
    TABLE_OPERATION = "table_operation"
    PAGINATION = "pagination"
    INFINITE_SCROLL = "infinite_scroll"
    SEARCH_FILTER = "search_filter"
    
    # 文件操作
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"
    DRAG_DROP = "drag_drop"
    
    # 输入增强
    AUTOCOMPLETE = "autocomplete"
    DATE_PICKER = "date_picker"
    RICH_TEXT_EDITOR = "rich_text_editor"
    
    # 状态管理
    LOADING_STATE = "loading_state"
    ERROR_STATE = "error_state"
    EMPTY_STATE = "empty_state"
    
    # 用户操作
    USER_AUTH = "user_auth"
    USER_PROFILE = "user_profile"
    
    # API 场景
    API_CRUD = "api_crud"
    API_SEARCH = "api_search"
    API_PAGINATION = "api_pagination"


@dataclass
class DetectedScenario:
    """检测到的场景"""
    type: ScenarioType
    name: str
    description: str
    elements: List[Dict] = field(default_factory=list)
    priority: str = "P1"
    test_count_estimate: int = 3
    complexity: str = "medium"


class ScenarioDetector:
    """场景检测器"""
    
    def __init__(self):
        self.detection_rules = self._init_rules()
    
    def _init_rules(self) -> Dict[str, Dict]:
        """初始化检测规则"""
        return {
            'modal': {
                'selectors': ['[role="dialog"]', '.modal', '[aria-modal="true"]'],
                'attributes': ['aria-modal'],
                'scenario_type': ScenarioType.MODAL_DIALOG
            },
            'dropdown': {
                'selectors': ['[role="listbox"]', '[role="combobox"]', 'select', '.dropdown'],
                'attributes': ['aria-expanded', 'aria-haspopup'],
                'scenario_type': ScenarioType.DROPDOWN_SELECT
            },
            'tabs': {
                'selectors': ['[role="tablist"]', '.tabs', '.tab-panel'],
                'attributes': ['aria-selected'],
                'scenario_type': ScenarioType.TAB_NAVIGATION
            },
            'table': {
                'selectors': ['table', '[role="grid"]', '.data-table'],
                'attributes': ['aria-sort'],
                'scenario_type': ScenarioType.TABLE_OPERATION
            },
            'pagination': {
                'selectors': ['.pagination', '[aria-label*="pagination"]', '.pager'],
                'keywords': ['page', 'next', 'prev', '上一页', '下一页'],
                'scenario_type': ScenarioType.PAGINATION
            },
            'file_upload': {
                'selectors': ['input[type="file"]', '.upload', '.dropzone'],
                'attributes': ['accept'],
                'scenario_type': ScenarioType.FILE_UPLOAD
            },
            'date_picker': {
                'selectors': ['input[type="date"]', '.datepicker', '.calendar'],
                'keywords': ['date', 'calendar', '日期'],
                'scenario_type': ScenarioType.DATE_PICKER
            },
            'search': {
                'selectors': ['input[type="search"]', '[role="searchbox"]', '.search'],
                'keywords': ['search', '搜索', 'query'],
                'scenario_type': ScenarioType.SEARCH_FILTER
            },
            'autocomplete': {
                'selectors': ['[role="combobox"]', '.autocomplete', '[aria-autocomplete]'],
                'attributes': ['aria-autocomplete'],
                'scenario_type': ScenarioType.AUTOCOMPLETE
            },
            'form': {
                'selectors': ['form', '[role="form"]'],
                'has_children': ['input', 'button[type="submit"]'],
                'scenario_type': ScenarioType.FORM_SUBMIT
            },
            'login': {
                'keywords': ['login', 'signin', 'password', '登录', '密码'],
                'has_fields': ['password'],
                'scenario_type': ScenarioType.USER_AUTH
            }
        }
    
    def detect(self, elements: Dict[str, List], 
               api_requests: List[Dict] = None) -> List[DetectedScenario]:
        """
        检测页面中的场景
        
        Args:
            elements: 页面元素（从 WebpageAnalyzer 获取）
            api_requests: API 请求列表
        
        Returns:
            检测到的场景列表
        """
        scenarios = []
        
        # 检测 UI 场景
        scenarios.extend(self._detect_ui_scenarios(elements))
        
        # 检测 API 场景
        if api_requests:
            scenarios.extend(self._detect_api_scenarios(api_requests))
        
        # 去重和优先级排序
        scenarios = self._deduplicate(scenarios)
        scenarios.sort(key=lambda s: (self._priority_order(s.priority), s.name))
        
        return scenarios
    
    def detect_from_analysis(self, analysis) -> List[DetectedScenario]:
        """
        从分析结果检测场景（便捷方法）
        
        Args:
            analysis: WebpageAnalyzer 或 FigmaAnalyzer 的分析结果
                     可以是 dict 或 dataclass
        
        Returns:
            检测到的场景列表
        """
        # 支持 dict 和 dataclass 两种格式
        if hasattr(analysis, '__dict__'):
            # dataclass 或对象
            elements = getattr(analysis, 'elements', {})
            api_requests = getattr(analysis, 'api_requests', [])
        else:
            # dict
            elements = analysis.get('elements', {})
            api_requests = analysis.get('api_requests', [])
        
        # 如果 elements 是 dict of lists of PageElement, 需要转换
        if elements and isinstance(next(iter(elements.values()), None), list):
            first_elem = next((e for es in elements.values() for e in es), None)
            if first_elem and hasattr(first_elem, '__dict__'):
                # 转换 PageElement 到 dict
                elements = {
                    k: [e.__dict__ if hasattr(e, '__dict__') else e for e in v]
                    for k, v in elements.items()
                }
        
        return self.detect(elements, api_requests)
    
    def _detect_ui_scenarios(self, elements: Dict) -> List[DetectedScenario]:
        """检测 UI 场景"""
        scenarios = []
        
        # 检测模态框
        if elements.get('modals'):
            scenarios.append(DetectedScenario(
                type=ScenarioType.MODAL_DIALOG,
                name="模态框交互",
                description="打开/关闭模态框，验证内容显示和关闭行为",
                elements=elements['modals'],
                priority="P1",
                test_count_estimate=5
            ))
        
        # 检测标签页
        if elements.get('tabs'):
            scenarios.append(DetectedScenario(
                type=ScenarioType.TAB_NAVIGATION,
                name="标签页切换",
                description="切换标签页，验证内容切换和状态保持",
                elements=elements['tabs'],
                priority="P1",
                test_count_estimate=4
            ))
        
        # 检测表格
        if elements.get('tables'):
            scenarios.append(DetectedScenario(
                type=ScenarioType.TABLE_OPERATION,
                name="表格操作",
                description="表格排序、筛选、分页等操作",
                elements=elements['tables'],
                priority="P1",
                test_count_estimate=8
            ))
        
        # 检测下拉框
        if elements.get('selects'):
            scenarios.append(DetectedScenario(
                type=ScenarioType.DROPDOWN_SELECT,
                name="下拉选择",
                description="下拉框展开、选择、搜索等操作",
                elements=elements['selects'],
                priority="P2",
                test_count_estimate=4
            ))
        
        # 检测表单
        inputs = elements.get('inputs', [])
        buttons = elements.get('buttons', [])
        
        if inputs and buttons:
            # 检测登录表单
            has_password = any(i.get('type') == 'password' for i in inputs)
            if has_password:
                scenarios.append(DetectedScenario(
                    type=ScenarioType.USER_AUTH,
                    name="用户登录",
                    description="登录功能，包括正常登录、异常处理、记住密码等",
                    elements=inputs + buttons,
                    priority="P0",
                    test_count_estimate=12,
                    complexity="medium"
                ))
            else:
                scenarios.append(DetectedScenario(
                    type=ScenarioType.FORM_SUBMIT,
                    name="表单提交",
                    description="表单填写和提交，包括验证和错误处理",
                    elements=inputs + buttons,
                    priority="P1",
                    test_count_estimate=10
                ))
        
        # 检测文件上传
        file_inputs = [i for i in inputs if i.get('type') == 'file']
        if file_inputs:
            scenarios.append(DetectedScenario(
                type=ScenarioType.FILE_UPLOAD,
                name="文件上传",
                description="文件选择、上传、进度显示、错误处理",
                elements=file_inputs,
                priority="P1",
                test_count_estimate=6
            ))
        
        # 检测日期选择器
        date_inputs = [i for i in inputs if i.get('type') == 'date']
        if date_inputs:
            scenarios.append(DetectedScenario(
                type=ScenarioType.DATE_PICKER,
                name="日期选择",
                description="日期选择、范围限制、格式验证",
                elements=date_inputs,
                priority="P2",
                test_count_estimate=5
            ))
        
        # 检测搜索
        search_inputs = [i for i in inputs if i.get('type') == 'search' or 
                        'search' in (i.get('name') or '').lower() or
                        'search' in (i.get('placeholder') or '').lower()]
        if search_inputs:
            scenarios.append(DetectedScenario(
                type=ScenarioType.SEARCH_FILTER,
                name="搜索功能",
                description="关键词搜索、筛选、清空、搜索历史",
                elements=search_inputs,
                priority="P1",
                test_count_estimate=6
            ))
        
        # 检测链接导航
        links = elements.get('links', [])
        if links:
            scenarios.append(DetectedScenario(
                type=ScenarioType.NAVIGATION,
                name="链接导航",
                description="验证页面链接可点击、跳转正确、无死链",
                elements=links,
                priority="P2",
                test_count_estimate=len(links) * 2
            ))
        
        # 检测按钮（即使没有输入框）
        if buttons and not inputs:
            scenarios.append(DetectedScenario(
                type=ScenarioType.BUTTON_CLICK,
                name="按钮交互",
                description="按钮点击、状态变化、响应验证",
                elements=buttons,
                priority="P2",
                test_count_estimate=len(buttons) * 3
            ))
        
        # 如果页面很简单，生成基础页面测试
        if not scenarios:
            scenarios.append(DetectedScenario(
                type=ScenarioType.PAGE_LOAD,
                name="页面加载",
                description="页面正常加载、元素显示、无报错",
                elements=[],
                priority="P1",
                test_count_estimate=3
            ))
        
        return scenarios
    
    def _detect_api_scenarios(self, api_requests: List[Dict]) -> List[DetectedScenario]:
        """检测 API 场景"""
        scenarios = []
        
        methods = set(req.get('method', '').upper() for req in api_requests)
        
        # CRUD 场景
        if methods.intersection({'GET', 'POST', 'PUT', 'DELETE'}):
            scenarios.append(DetectedScenario(
                type=ScenarioType.API_CRUD,
                name="API 增删改查",
                description="API 接口的 CRUD 操作测试",
                priority="P1",
                test_count_estimate=8,
                complexity="medium"
            ))
        
        # 搜索 API
        search_apis = [r for r in api_requests if 
                      'search' in r.get('url', '').lower() or
                      'query' in r.get('url', '').lower()]
        if search_apis:
            scenarios.append(DetectedScenario(
                type=ScenarioType.API_SEARCH,
                name="搜索接口",
                description="搜索 API 的各种查询场景",
                priority="P1",
                test_count_estimate=6
            ))
        
        # 分页 API
        pagination_apis = [r for r in api_requests if 
                         'page' in r.get('url', '').lower() or
                         'limit' in r.get('url', '').lower()]
        if pagination_apis:
            scenarios.append(DetectedScenario(
                type=ScenarioType.API_PAGINATION,
                name="分页接口",
                description="分页 API 的边界和异常测试",
                priority="P2",
                test_count_estimate=5
            ))
        
        return scenarios
    
    def _deduplicate(self, scenarios: List[DetectedScenario]) -> List[DetectedScenario]:
        """去重"""
        seen = set()
        unique = []
        for s in scenarios:
            key = (s.type, s.name)
            if key not in seen:
                seen.add(key)
                unique.append(s)
        return unique
    
    def _priority_order(self, priority: str) -> int:
        """优先级排序"""
        order = {'P0': 0, 'P1': 1, 'P2': 2, 'P3': 3}
        return order.get(priority, 4)
