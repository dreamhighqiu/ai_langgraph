"""
功能测试用例生成器
根据分析结果自动生成结构化的功能测试用例
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class Priority(Enum):
    """优先级"""
    P0 = "P0"  # 阻塞级
    P1 = "P1"  # 高优先级
    P2 = "P2"  # 中优先级
    P3 = "P3"  # 低优先级


class TestType(Enum):
    """测试类型"""
    FUNCTIONAL = "functional"    # 功能测试
    UI = "ui"                    # UI测试
    BOUNDARY = "boundary"        # 边界值测试
    NEGATIVE = "negative"        # 异常测试
    SECURITY = "security"        # 安全测试
    PERFORMANCE = "performance"  # 性能测试


@dataclass
class TestStep:
    """测试步骤"""
    order: int
    action: str
    expected: str
    data: Optional[str] = None
    locator: Optional[str] = None  # 新增：每个步骤的定位器


@dataclass
class TestCase:
    """测试用例"""
    id: str
    module: str
    title: str
    priority: Priority
    type: TestType
    preconditions: List[str] = field(default_factory=list)
    steps: List[TestStep] = field(default_factory=list)
    test_data: Dict[str, Any] = field(default_factory=dict)
    expected_result: str = ""
    tags: List[str] = field(default_factory=list)
    status: str = "未执行"
    locators: List[str] = field(default_factory=list)  # 新增：所有步骤的定位器列表
    
    def to_dict(self) -> Dict:
        # 将步骤格式化为简单的 "1. 操作 -> 预期" 格式
        steps_text = [
            f"{s.order}. {s.action}" + (f" -> {s.expected}" if s.expected else "")
            for s in self.steps
        ]
        
        # 提取所有步骤的定位器
        locators = []
        for step in self.steps:
            if hasattr(step, 'locator') and step.locator:
                locators.append(step.locator)
            else:
                locators.append("")  # 步骤没有定位器时用空字符串
        
        # 如果 self.locators 有值，使用它；否则使用从 steps 提取的
        final_locators = self.locators if self.locators else locators
        
        return {
            'id': self.id,
            'module': self.module,
            'title': self.title,
            'priority': self.priority.value,
            'type': self.type.value,
            'preconditions': self.preconditions,
            'steps': steps_text,  # 简化为字符串列表
            'locators': final_locators,  # 新增：定位器列表
            'test_data': self.test_data,
            'expected_result': self.expected_result,
            'tags': self.tags,
            'status': self.status
        }


class TestCaseGenerator:
    """功能测试用例生成器"""
    
    def __init__(self, config: Dict = None):
        """
        Args:
            config: 配置字典
                - ui_only: 只生成UI功能测试用例，过滤性能/安全/边界值等测试（默认True）
                - include_negative: 是否包含异常测试用例（默认False）
        """
        self.config = config or {}
        self.ui_only = self.config.get('ui_only', True)  # 默认只生成UI功能测试
        self.include_negative = self.config.get('include_negative', False)  # 默认不包含异常测试
        self.test_cases: List[TestCase] = []
        self.case_counter = 0
    
    def _should_include_test_case(self, test_case: TestCase) -> bool:
        """判断是否应该包含该测试用例
        
        Args:
            test_case: 测试用例
        
        Returns:
            bool: 是否包含
        """
        if not self.ui_only:
            return True
        
        # UI功能测试模式：只保留FUNCTIONAL和UI类型
        if test_case.type in [TestType.FUNCTIONAL, TestType.UI]:
            return True
        
        # 如果包含异常测试，也保留NEGATIVE类型
        if self.include_negative and test_case.type == TestType.NEGATIVE:
            return True
        
        # 过滤掉BOUNDARY, SECURITY, PERFORMANCE类型
        return False
    
    def _extract_locator_from_element(self, element: Any) -> str:
        """从元素中提取Playwright定位器
        
        Args:
            element: 页面元素（可能是PageElement对象或字典）
        
        Returns:
            str: Playwright定位器字符串
        """
        if element is None:
            return ""
        
        # 如果是字典
        if isinstance(element, dict):
            # 直接有locator字段
            if 'locator' in element:
                return element['locator']
            
            # 根据属性生成定位器
            if 'data_testid' in element and element.get('data_testid'):
                return f"page.get_by_test_id('{element['data_testid']}')"
            elif 'aria_label' in element and element.get('aria_label'):
                return f"page.get_by_label('{element['aria_label']}')"
            elif 'role' in element and element.get('role'):
                role = element['role']
                text = element.get('text', '').strip()
                if text:
                    return f"page.get_by_role('{role}', name='{text[:50]}')"
                return f"page.get_by_role('{role}')"
            elif 'placeholder' in element and element.get('placeholder'):
                return f"page.get_by_placeholder('{element['placeholder']}')"
            elif 'text' in element and element.get('text', '').strip():
                text = element['text'].strip()[:50]
                return f"page.get_by_text('{text}')"
            elif 'name' in element and element.get('name'):
                return f"page.get_by_label('{element['name']}')"
            elif 'id' in element and element.get('id'):
                return f"page.locator('#{element['id']}')"
        
        # 如果是PageElement对象
        elif hasattr(element, 'locator'):
            return element.locator or ""
        
        return ""
    
    def generate_from_scenarios(self, scenarios: List[Any], 
                                module_name: str = "Main") -> List[TestCase]:
        """
        从检测到的场景生成测试用例
        
        Args:
            scenarios: DetectedScenario 列表
            module_name: 模块名称
        
        Returns:
            TestCase 列表
        """
        test_cases = []
        
        for scenario in scenarios:
            cases = self._generate_for_scenario(scenario, module_name)
            # 应用过滤逻辑
            if self.ui_only:
                cases = [tc for tc in cases if self._should_include_test_case(tc)]
            test_cases.extend(cases)
        
        self.test_cases.extend(test_cases)
        return test_cases
    
    def generate_from_elements(self, elements: Dict[str, List],
                               page_name: str = "Page") -> List[TestCase]:
        """
        从页面元素直接生成测试用例
        
        Args:
            elements: 页面元素字典
            page_name: 页面名称
        
        Returns:
            TestCase 列表
        """
        test_cases = []
        
        # 输入框测试
        for input_el in elements.get('inputs', []):
            cases = self._generate_input_tests(input_el, page_name)
            test_cases.extend(cases)
        
        # 按钮测试
        for button in elements.get('buttons', []):
            cases = self._generate_button_tests(button, page_name)
            test_cases.extend(cases)
        
        # 链接测试
        for link in elements.get('links', []):
            cases = self._generate_link_tests(link, page_name)
            test_cases.extend(cases)
        
        self.test_cases.extend(test_cases)
        return test_cases
    
    def _generate_for_scenario(self, scenario, module_name: str) -> List[TestCase]:
        """为单个场景生成测试用例"""
        cases = []
        scenario_type = scenario.type.value if hasattr(scenario.type, 'value') else str(scenario.type)
        
        # 根据场景类型生成不同的测试用例
        if 'auth' in scenario_type or 'login' in scenario_type.lower():
            cases.extend(self._generate_auth_tests(scenario, module_name))
        elif 'form' in scenario_type:
            cases.extend(self._generate_form_tests(scenario, module_name))
        elif 'modal' in scenario_type:
            cases.extend(self._generate_modal_tests(scenario, module_name))
        elif 'table' in scenario_type:
            cases.extend(self._generate_table_tests(scenario, module_name))
        elif 'search' in scenario_type:
            cases.extend(self._generate_search_tests(scenario, module_name))
        elif 'upload' in scenario_type:
            cases.extend(self._generate_upload_tests(scenario, module_name))
        elif 'navigation' in scenario_type:
            cases.extend(self._generate_navigation_tests(scenario, module_name))
        elif 'button' in scenario_type:
            cases.extend(self._generate_button_click_tests(scenario, module_name))
        elif 'page_load' in scenario_type:
            cases.extend(self._generate_page_load_tests(scenario, module_name))
        else:
            # 通用场景测试
            cases.extend(self._generate_generic_tests(scenario, module_name))
        
        return cases
    
    def _generate_navigation_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成链接导航测试用例"""
        cases = []
        base_id = self._next_id(module_name, "NAV")
        elements = getattr(scenario, 'elements', [])
        
        for i, link in enumerate(elements[:5], 1):  # 限制最多5个链接
            link_text = link.get('text', f'Link {i}') if isinstance(link, dict) else f'Link {i}'
            link_href = link.get('href', '#') if isinstance(link, dict) else '#'
            locator = self._extract_locator_from_element(link)
            
            cases.append(TestCase(
                id=f"{base_id}_{i:03d}",
                module=module_name,
                title=f"链接导航 - {link_text[:30]}",
                priority=Priority.P2,
                type=TestType.FUNCTIONAL,
                preconditions=["页面加载完成"],
                steps=[
                    TestStep(1, f"定位链接 '{link_text}'", "链接可见", locator=locator),
                    TestStep(2, "点击链接", "页面跳转或打开新窗口", locator=locator),
                    TestStep(3, "验证目标页面", "目标页面正确加载", locator="")
                ],
                test_data={"link_text": link_text, "href": link_href},
                expected_result=f"成功导航到 {link_href}",
                locators=[locator, locator, ""]  # 每个步骤的定位器
            ))
        
        # 死链检测
        cases.append(TestCase(
            id=f"{base_id}_DL",
            module=module_name,
            title="死链检测 - 验证所有链接有效",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            preconditions=["页面加载完成"],
            steps=[
                TestStep(1, "获取页面所有链接", "链接列表"),
                TestStep(2, "逐一访问每个链接", "记录响应状态"),
                TestStep(3, "验证无404或500错误", "所有链接有效")
            ],
            expected_result="所有链接返回有效响应（非404/500）"
        ))
        
        return cases
    
    def _generate_button_click_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成按钮点击测试用例"""
        cases = []
        base_id = self._next_id(module_name, "BTN")
        elements = getattr(scenario, 'elements', [])
        
        for i, btn in enumerate(elements[:5], 1):
            btn_text = btn.get('text', f'Button {i}') if isinstance(btn, dict) else f'Button {i}'
            locator = self._extract_locator_from_element(btn)
            
            cases.append(TestCase(
                id=f"{base_id}_{i:03d}",
                module=module_name,
                title=f"按钮点击 - {btn_text[:30]}",
                priority=Priority.P2,
                type=TestType.FUNCTIONAL,
                preconditions=["页面加载完成", "按钮可见且可点击"],
                steps=[
                    TestStep(1, f"定位按钮 '{btn_text}'", "按钮可见", locator=locator),
                    TestStep(2, "点击按钮", "触发相应操作", locator=locator),
                    TestStep(3, "验证响应", "操作成功完成", locator="")
                ],
                expected_result=f"点击 '{btn_text}' 按钮后执行预期操作",
                locators=[locator, locator, ""]
            ))
        
        return cases
    
    def _generate_page_load_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成页面加载测试用例"""
        cases = []
        base_id = self._next_id(module_name, "PG")
        
        # 页面加载成功
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="页面加载 - 正常加载验证",
            priority=Priority.P0,
            type=TestType.FUNCTIONAL,
            preconditions=["网络正常", "服务器正常运行"],
            steps=[
                TestStep(1, "访问页面 URL", "开始加载"),
                TestStep(2, "等待页面加载完成", "页面渲染完成"),
                TestStep(3, "验证页面标题", "标题正确显示"),
                TestStep(4, "验证主要元素可见", "关键元素已渲染")
            ],
            expected_result="页面在合理时间内加载完成，无报错"
        ))
        
        # 控制台错误检查
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="页面加载 - 无控制台错误",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            preconditions=["页面加载完成"],
            steps=[
                TestStep(1, "打开浏览器开发者工具", "Console 面板"),
                TestStep(2, "刷新页面", "页面重新加载"),
                TestStep(3, "检查控制台", "查看是否有错误")
            ],
            expected_result="控制台无 JavaScript 错误"
        ))
        
        # 响应式布局
        cases.append(TestCase(
            id=f"{base_id}_003",
            module=module_name,
            title="页面加载 - 响应式布局",
            priority=Priority.P2,
            type=TestType.UI,
            preconditions=["页面加载完成"],
            steps=[
                TestStep(1, "在桌面分辨率查看", "布局正常"),
                TestStep(2, "调整为平板分辨率", "布局自适应"),
                TestStep(3, "调整为手机分辨率", "布局自适应")
            ],
            expected_result="页面在不同分辨率下正常显示"
        ))
        
        return cases
    
    def _generate_auth_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成认证相关测试用例"""
        cases = []
        base_id = self._next_id(module_name, "AUTH")
        
        # 正常登录
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="正常登录 - 使用有效凭据",
            priority=Priority.P0,
            type=TestType.FUNCTIONAL,
            preconditions=["用户已注册", "账号状态正常", "在登录页面"],
            steps=[
                TestStep(1, "输入正确的用户名", "用户名显示在输入框中"),
                TestStep(2, "输入正确的密码", "密码以掩码显示"),
                TestStep(3, "点击登录按钮", "登录成功，跳转到首页")
            ],
            test_data={"username": "valid_user@test.com", "password": "ValidPass123!"},
            expected_result="登录成功，显示用户信息"
        ))
        
        # 密码错误
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="登录失败 - 密码错误",
            priority=Priority.P0,
            type=TestType.NEGATIVE,
            preconditions=["用户已注册", "在登录页面"],
            steps=[
                TestStep(1, "输入正确的用户名", "用户名显示正常"),
                TestStep(2, "输入错误的密码", "密码以掩码显示"),
                TestStep(3, "点击登录按钮", "登录失败，显示错误提示")
            ],
            test_data={"username": "valid_user@test.com", "password": "WrongPassword"},
            expected_result="显示'用户名或密码错误'提示"
        ))
        
        # 用户名为空
        cases.append(TestCase(
            id=f"{base_id}_003",
            module=module_name,
            title="登录失败 - 用户名为空",
            priority=Priority.P1,
            type=TestType.NEGATIVE,
            preconditions=["在登录页面"],
            steps=[
                TestStep(1, "保持用户名为空", "输入框为空或显示占位符"),
                TestStep(2, "输入密码", "密码以掩码显示"),
                TestStep(3, "点击登录按钮", "显示用户名必填提示")
            ],
            expected_result="显示用户名必填的验证提示"
        ))
        
        # 密码为空
        cases.append(TestCase(
            id=f"{base_id}_004",
            module=module_name,
            title="登录失败 - 密码为空",
            priority=Priority.P1,
            type=TestType.NEGATIVE,
            preconditions=["在登录页面"],
            steps=[
                TestStep(1, "输入用户名", "用户名显示正常"),
                TestStep(2, "保持密码为空", "密码输入框为空"),
                TestStep(3, "点击登录按钮", "显示密码必填提示")
            ],
            expected_result="显示密码必填的验证提示"
        ))
        
        # SQL注入测试
        cases.append(TestCase(
            id=f"{base_id}_005",
            module=module_name,
            title="安全测试 - SQL注入防护",
            priority=Priority.P1,
            type=TestType.SECURITY,
            preconditions=["在登录页面"],
            steps=[
                TestStep(1, "在用户名输入SQL注入语句", "输入框显示注入内容"),
                TestStep(2, "输入任意密码", "密码以掩码显示"),
                TestStep(3, "点击登录按钮", "系统拒绝登录，不执行注入")
            ],
            test_data={"username": "' OR '1'='1", "password": "anything"},
            expected_result="登录失败，系统未被注入"
        ))
        
        return cases
    
    def _generate_form_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成表单相关测试用例"""
        cases = []
        base_id = self._next_id(module_name, "FORM")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="表单提交 - 填写所有必填字段",
            priority=Priority.P0,
            type=TestType.FUNCTIONAL,
            preconditions=["在表单页面", "表单为空状态"],
            steps=[
                TestStep(1, "填写所有必填字段", "字段显示输入值"),
                TestStep(2, "点击提交按钮", "表单验证通过并提交")
            ],
            expected_result="表单提交成功，显示成功提示"
        ))
        
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="表单提交 - 必填字段为空",
            priority=Priority.P1,
            type=TestType.NEGATIVE,
            preconditions=["在表单页面"],
            steps=[
                TestStep(1, "保持必填字段为空", "字段为空"),
                TestStep(2, "点击提交按钮", "显示验证错误")
            ],
            expected_result="显示必填字段验证错误提示"
        ))
        
        return cases
    
    def _generate_modal_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成模态框测试用例"""
        cases = []
        base_id = self._next_id(module_name, "MODAL")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="模态框 - 打开和关闭",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "触发打开模态框", "模态框显示"),
                TestStep(2, "点击关闭按钮", "模态框关闭")
            ],
            expected_result="模态框正常打开和关闭"
        ))
        
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="模态框 - 点击遮罩关闭",
            priority=Priority.P2,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "打开模态框", "模态框显示"),
                TestStep(2, "点击模态框外部遮罩区域", "模态框关闭")
            ],
            expected_result="点击遮罩时模态框关闭"
        ))
        
        return cases
    
    def _generate_table_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成表格测试用例"""
        cases = []
        base_id = self._next_id(module_name, "TABLE")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="表格 - 数据展示",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "加载表格页面", "表格数据正常显示")
            ],
            expected_result="表格正确展示数据"
        ))
        
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="表格 - 排序功能",
            priority=Priority.P2,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "点击表头排序按钮", "数据按该列排序")
            ],
            expected_result="数据正确排序"
        ))
        
        return cases
    
    def _generate_search_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成搜索测试用例"""
        cases = []
        base_id = self._next_id(module_name, "SEARCH")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="搜索 - 关键词搜索",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "输入搜索关键词", "关键词显示在搜索框"),
                TestStep(2, "触发搜索", "显示搜索结果")
            ],
            expected_result="显示与关键词匹配的结果"
        ))
        
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="搜索 - 无结果处理",
            priority=Priority.P2,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "输入不存在的关键词", "关键词显示在搜索框"),
                TestStep(2, "触发搜索", "显示无结果提示")
            ],
            test_data={"keyword": "zzz_not_exist_xxx"},
            expected_result="显示'无搜索结果'提示"
        ))
        
        return cases
    
    def _generate_upload_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成上传测试用例"""
        cases = []
        base_id = self._next_id(module_name, "UPLOAD")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title="文件上传 - 上传有效文件",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, "选择有效文件", "文件名显示"),
                TestStep(2, "点击上传", "上传成功")
            ],
            expected_result="文件上传成功"
        ))
        
        cases.append(TestCase(
            id=f"{base_id}_002",
            module=module_name,
            title="文件上传 - 文件类型限制",
            priority=Priority.P1,
            type=TestType.NEGATIVE,
            steps=[
                TestStep(1, "选择不支持的文件类型", "显示文件类型错误")
            ],
            expected_result="提示文件类型不支持"
        ))
        
        return cases
    
    def _generate_generic_tests(self, scenario, module_name: str) -> List[TestCase]:
        """生成通用测试用例"""
        cases = []
        base_id = self._next_id(module_name, "GEN")
        
        cases.append(TestCase(
            id=f"{base_id}_001",
            module=module_name,
            title=f"{scenario.name} - 基本功能",
            priority=Priority.P1,
            type=TestType.FUNCTIONAL,
            steps=[
                TestStep(1, f"执行{scenario.name}操作", "操作成功")
            ],
            expected_result="功能正常运行"
        ))
        
        return cases
    
    def _generate_input_tests(self, input_el: Dict, page_name: str) -> List[TestCase]:
        """为输入框生成测试"""
        cases = []
        input_name = input_el.get('name') or input_el.get('id') or 'input'
        input_type = input_el.get('type', 'text')
        base_id = self._next_id(page_name, "INPUT")
        
        # 必填验证
        if input_el.get('required'):
            cases.append(TestCase(
                id=f"{base_id}_001",
                module=page_name,
                title=f"输入框验证 - {input_name} 必填",
                priority=Priority.P1,
                type=TestType.NEGATIVE,
                steps=[
                    TestStep(1, f"保持 {input_name} 为空", "输入框为空"),
                    TestStep(2, "提交表单", "显示必填验证错误")
                ],
                expected_result="显示必填字段验证提示"
            ))
        
        return cases
    
    def _generate_button_tests(self, button: Dict, page_name: str) -> List[TestCase]:
        """为按钮生成测试"""
        cases = []
        button_text = button.get('text', '') or button.get('name', 'button')
        base_id = self._next_id(page_name, "BTN")
        
        if not button.get('disabled'):
            cases.append(TestCase(
                id=f"{base_id}_001",
                module=page_name,
                title=f"按钮点击 - {button_text}",
                priority=Priority.P2,
                type=TestType.FUNCTIONAL,
                steps=[
                    TestStep(1, f"点击 {button_text} 按钮", "触发相应操作")
                ],
                expected_result="按钮响应正常"
            ))
        
        return cases
    
    def _generate_link_tests(self, link: Dict, page_name: str) -> List[TestCase]:
        """为链接生成测试"""
        # 只为重要链接生成测试
        return []
    
    def _next_id(self, module: str, category: str) -> str:
        """生成下一个测试用例ID"""
        self.case_counter += 1
        return f"TC_{module.upper()}_{category}_{self.case_counter:03d}"
    
    def get_all_cases(self) -> List[TestCase]:
        """获取所有测试用例"""
        return self.test_cases
    
    def get_summary(self) -> Dict:
        """获取摘要统计"""
        return {
            'total': len(self.test_cases),
            'by_priority': {
                'P0': len([c for c in self.test_cases if c.priority == Priority.P0]),
                'P1': len([c for c in self.test_cases if c.priority == Priority.P1]),
                'P2': len([c for c in self.test_cases if c.priority == Priority.P2]),
                'P3': len([c for c in self.test_cases if c.priority == Priority.P3])
            },
            'by_type': {
                t.value: len([c for c in self.test_cases if c.type == t])
                for t in TestType
            }
        }
