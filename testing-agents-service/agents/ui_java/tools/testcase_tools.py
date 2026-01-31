"""
测试用例生成工具

基于测试计划生成结构化的功能测试用例
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path


class Priority(Enum):
    """测试优先级"""
    P0 = "P0"  # 阻塞级 - 核心功能
    P1 = "P1"  # 高优先级 - 重要功能
    P2 = "P2"  # 中优先级 - 一般功能
    P3 = "P3"  # 低优先级 - 边缘功能


class TestType(Enum):
    """测试类型"""
    FUNCTIONAL = "functional"    # 功能测试
    UI = "ui"                    # UI 测试
    BOUNDARY = "boundary"        # 边界值测试
    NEGATIVE = "negative"        # 异常/负向测试
    SECURITY = "security"        # 安全测试
    PERFORMANCE = "performance"  # 性能测试
    SMOKE = "smoke"              # 冒烟测试
    REGRESSION = "regression"    # 回归测试


@dataclass
class TestStep:
    """测试步骤"""
    order: int
    action: str
    expected: str
    data: Optional[str] = None
    locator: Optional[str] = None  # Playwright 定位器


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
    locators: List[str] = field(default_factory=list)
    url: str = ""
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        steps_text = []
        locators = []
        
        for s in self.steps:
            step_str = f"{s.order}. {s.action}"
            if s.expected:
                step_str += f" -> {s.expected}"
            steps_text.append(step_str)
            locators.append(s.locator or "")
        
        return {
            'id': self.id,
            'module': self.module,
            'title': self.title,
            'priority': self.priority.value,
            'type': self.type.value,
            'preconditions': self.preconditions,
            'steps': steps_text,
            'steps_detail': [
                {
                    'order': s.order,
                    'action': s.action,
                    'expected': s.expected,
                    'data': s.data,
                    'locator': s.locator
                }
                for s in self.steps
            ],
            'locators': self.locators if self.locators else locators,
            'test_data': self.test_data,
            'expected_result': self.expected_result,
            'tags': self.tags,
            'status': self.status,
            'url': self.url
        }
    
    def to_java_test_method(self) -> str:
        """生成 Java 测试方法框架"""
        method_name = self._to_method_name(self.title)
        tags = ', '.join([f'@Tag("{tag}")' for tag in self.tags]) if self.tags else '@Tag("functional")'
        
        steps_comments = []
        for step in self.steps:
            comment = f"        // 步骤 {step.order}: {step.action}"
            if step.expected:
                comment += f" -> 预期: {step.expected}"
            steps_comments.append(comment)
            if step.locator:
                steps_comments.append(f"        // 定位器: {step.locator}")
            steps_comments.append("        // TODO: 实现步骤")
            steps_comments.append("")
        
        return f'''
    /**
     * {self.title}
     * 用例ID: {self.id}
     * 优先级: {self.priority.value}
     * 前置条件: {', '.join(self.preconditions) if self.preconditions else '无'}
     */
    {tags}
    @Test
    void {method_name}() throws InterruptedException {{
{chr(10).join(steps_comments)}
        // 验证: {self.expected_result}
    }}
'''
    
    def _to_method_name(self, title: str) -> str:
        """将标题转换为方法名"""
        # 移除特殊字符，转换为驼峰命名
        clean = re.sub(r'[^\w\s]', '', title)
        words = clean.split()
        if not words:
            return "testCase"
        
        # 首字母小写的驼峰命名
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        
        # 确保以 test 开头
        if not result.startswith('test'):
            result = 'test' + result[0].upper() + result[1:]
        
        return result


class TestCaseGenerator:
    """测试用例生成器"""
    
    def __init__(self, config: Dict = None):
        """
        初始化生成器
        
        Args:
            config: 配置字典
                - ui_only: 只生成 UI 功能测试用例（默认 False）
                - include_negative: 包含异常测试用例（默认 True）
                - include_boundary: 包含边界值测试（默认 True）
        """
        self.config = config or {}
        self.ui_only = self.config.get('ui_only', False)
        self.include_negative = self.config.get('include_negative', True)
        self.include_boundary = self.config.get('include_boundary', True)
        self.test_cases: List[TestCase] = []
        self.case_counter = 0
    
    def should_include_case(self, test_case: TestCase) -> bool:
        """判断是否应包含该测试用例"""
        if not self.ui_only:
            return True
        
        # UI 模式：只保留 FUNCTIONAL、UI、SMOKE 类型
        if test_case.type in [TestType.FUNCTIONAL, TestType.UI, TestType.SMOKE]:
            return True
        
        if self.include_negative and test_case.type == TestType.NEGATIVE:
            return True
        
        if self.include_boundary and test_case.type == TestType.BOUNDARY:
            return True
        
        return False
    
    def generate_from_plan(
        self,
        plan_content: str,
        module_name: str,
        url: str = ""
    ) -> List[TestCase]:
        """
        从测试计划内容生成测试用例
        
        Args:
            plan_content: 测试计划 Markdown 内容
            module_name: 模块名称
            url: 测试页面 URL
        
        Returns:
            生成的测试用例列表
        """
        cases = []
        
        # 解析测试计划
        scenarios = self._parse_plan_content(plan_content)
        
        for scenario in scenarios:
            scenario_cases = self._generate_scenario_cases(scenario, module_name, url)
            for tc in scenario_cases:
                if self.should_include_case(tc):
                    cases.append(tc)
        
        self.test_cases.extend(cases)
        return cases
    
    def _parse_plan_content(self, content: str) -> List[Dict]:
        """解析测试计划内容"""
        scenarios = []
        current_scenario = None
        
        lines = content.split('\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # 匹配场景标题 (## 或 ### 开头)
            if line.startswith('## ') or line.startswith('### '):
                if current_scenario:
                    scenarios.append(current_scenario)
                
                title = re.sub(r'^#+\s*', '', line)
                # 提取场景编号和名称
                match = re.match(r'(\d+\.?\d*)\s*(.+)', title)
                if match:
                    scenario_id = match.group(1)
                    scenario_name = match.group(2)
                else:
                    scenario_id = str(len(scenarios) + 1)
                    scenario_name = title
                
                current_scenario = {
                    'id': scenario_id,
                    'name': scenario_name,
                    'preconditions': [],
                    'steps': [],
                    'expected': '',
                    'priority': 'P1',
                    'type': 'functional'
                }
            
            # 匹配前置条件
            elif current_scenario and ('前置条件' in line or 'precondition' in line.lower()):
                # 获取后续的列表项
                i += 1
                while i < len(lines) and lines[i].strip().startswith('-'):
                    cond = lines[i].strip().lstrip('- ').strip()
                    current_scenario['preconditions'].append(cond)
                    i += 1
                continue
            
            # 匹配测试步骤
            elif current_scenario and ('步骤' in line or 'steps' in line.lower()):
                i += 1
                step_order = 1
                while i < len(lines):
                    step_line = lines[i].strip()
                    # 匹配数字开头的步骤
                    step_match = re.match(r'(\d+)\.\s*(.+)', step_line)
                    if step_match:
                        step_text = step_match.group(2)
                        current_scenario['steps'].append({
                            'order': step_order,
                            'action': step_text,
                            'expected': ''
                        })
                        step_order += 1
                        i += 1
                    elif step_line.startswith('-'):
                        # 也支持列表格式的步骤
                        step_text = step_line.lstrip('- ').strip()
                        current_scenario['steps'].append({
                            'order': step_order,
                            'action': step_text,
                            'expected': ''
                        })
                        step_order += 1
                        i += 1
                    else:
                        break
                continue
            
            # 匹配预期结果
            elif current_scenario and ('预期' in line or 'expected' in line.lower()):
                # 获取预期结果内容
                if ':' in line or '：' in line:
                    expected = re.split(r'[:：]', line, 1)[1].strip()
                    current_scenario['expected'] = expected
                else:
                    i += 1
                    if i < len(lines):
                        current_scenario['expected'] = lines[i].strip().lstrip('- ').strip()
            
            # 匹配优先级
            elif current_scenario and ('优先级' in line or 'priority' in line.lower()):
                match = re.search(r'P[0-3]', line, re.IGNORECASE)
                if match:
                    current_scenario['priority'] = match.group().upper()
            
            i += 1
        
        # 添加最后一个场景
        if current_scenario:
            scenarios.append(current_scenario)
        
        return scenarios
    
    def _generate_scenario_cases(
        self,
        scenario: Dict,
        module_name: str,
        url: str
    ) -> List[TestCase]:
        """为单个场景生成测试用例"""
        cases = []
        
        # 主功能测试
        main_case = self._create_case(
            module=module_name,
            title=scenario['name'],
            priority=self._parse_priority(scenario.get('priority', 'P1')),
            test_type=TestType.FUNCTIONAL,
            preconditions=scenario.get('preconditions', []),
            steps=scenario.get('steps', []),
            expected=scenario.get('expected', '功能正常'),
            tags=['functional', 'smoke'] if scenario.get('priority') == 'P0' else ['functional'],
            url=url
        )
        cases.append(main_case)
        
        # 根据场景类型生成额外测试用例
        scenario_name_lower = scenario['name'].lower()
        
        if '登录' in scenario_name_lower or 'login' in scenario_name_lower:
            cases.extend(self._generate_auth_additional_cases(scenario, module_name, url))
        elif '表单' in scenario_name_lower or 'form' in scenario_name_lower:
            cases.extend(self._generate_form_additional_cases(scenario, module_name, url))
        elif '搜索' in scenario_name_lower or 'search' in scenario_name_lower:
            cases.extend(self._generate_search_additional_cases(scenario, module_name, url))
        
        return cases
    
    def _create_case(
        self,
        module: str,
        title: str,
        priority: Priority,
        test_type: TestType,
        preconditions: List[str],
        steps: List[Dict],
        expected: str,
        tags: List[str],
        url: str = ""
    ) -> TestCase:
        """创建测试用例"""
        self.case_counter += 1
        case_id = f"TC_{module.upper()}_{self.case_counter:03d}"
        
        test_steps = []
        for step in steps:
            test_steps.append(TestStep(
                order=step.get('order', len(test_steps) + 1),
                action=step.get('action', ''),
                expected=step.get('expected', ''),
                data=step.get('data'),
                locator=step.get('locator')
            ))
        
        return TestCase(
            id=case_id,
            module=module,
            title=title,
            priority=priority,
            type=test_type,
            preconditions=preconditions,
            steps=test_steps,
            expected_result=expected,
            tags=tags,
            url=url
        )
    
    def _generate_auth_additional_cases(
        self,
        scenario: Dict,
        module: str,
        url: str
    ) -> List[TestCase]:
        """生成认证相关的额外测试用例"""
        cases = []
        
        if self.include_negative:
            # 密码错误
            cases.append(self._create_case(
                module=module,
                title="登录失败 - 密码错误",
                priority=Priority.P0,
                test_type=TestType.NEGATIVE,
                preconditions=["用户已注册", "在登录页面"],
                steps=[
                    {'order': 1, 'action': '输入正确的用户名', 'expected': '用户名显示正常'},
                    {'order': 2, 'action': '输入错误的密码', 'expected': '密码以掩码显示'},
                    {'order': 3, 'action': '点击登录按钮', 'expected': '显示错误提示'}
                ],
                expected="显示'用户名或密码错误'提示",
                tags=['negative', 'auth'],
                url=url
            ))
            
            # 用户名为空
            cases.append(self._create_case(
                module=module,
                title="登录失败 - 用户名为空",
                priority=Priority.P1,
                test_type=TestType.NEGATIVE,
                preconditions=["在登录页面"],
                steps=[
                    {'order': 1, 'action': '保持用户名为空', 'expected': '输入框显示占位符'},
                    {'order': 2, 'action': '输入密码', 'expected': '密码以掩码显示'},
                    {'order': 3, 'action': '点击登录按钮', 'expected': '显示验证提示'}
                ],
                expected="显示用户名必填的验证提示",
                tags=['negative', 'validation'],
                url=url
            ))
        
        return cases
    
    def _generate_form_additional_cases(
        self,
        scenario: Dict,
        module: str,
        url: str
    ) -> List[TestCase]:
        """生成表单相关的额外测试用例"""
        cases = []
        
        if self.include_negative:
            cases.append(self._create_case(
                module=module,
                title="表单提交 - 必填字段为空",
                priority=Priority.P1,
                test_type=TestType.NEGATIVE,
                preconditions=["在表单页面"],
                steps=[
                    {'order': 1, 'action': '保持必填字段为空', 'expected': '字段为空状态'},
                    {'order': 2, 'action': '点击提交按钮', 'expected': '显示验证错误'}
                ],
                expected="显示必填字段验证错误",
                tags=['negative', 'validation'],
                url=url
            ))
        
        if self.include_boundary:
            cases.append(self._create_case(
                module=module,
                title="表单提交 - 字段长度边界",
                priority=Priority.P2,
                test_type=TestType.BOUNDARY,
                preconditions=["在表单页面"],
                steps=[
                    {'order': 1, 'action': '输入超长文本到输入框', 'expected': '文本被截断或显示提示'},
                    {'order': 2, 'action': '点击提交按钮', 'expected': '验证字段长度'}
                ],
                expected="正确处理边界长度",
                tags=['boundary'],
                url=url
            ))
        
        return cases
    
    def _generate_search_additional_cases(
        self,
        scenario: Dict,
        module: str,
        url: str
    ) -> List[TestCase]:
        """生成搜索相关的额外测试用例"""
        cases = []
        
        # 空结果搜索
        cases.append(self._create_case(
            module=module,
            title="搜索 - 无结果处理",
            priority=Priority.P2,
            test_type=TestType.FUNCTIONAL,
            preconditions=["在搜索页面"],
            steps=[
                {'order': 1, 'action': '输入不存在的关键词', 'expected': '关键词显示在搜索框'},
                {'order': 2, 'action': '触发搜索', 'expected': '显示无结果提示'}
            ],
            expected="显示'无搜索结果'提示",
            tags=['functional', 'search'],
            url=url
        ))
        
        return cases
    
    def _parse_priority(self, priority_str: str) -> Priority:
        """解析优先级字符串"""
        priority_map = {
            'P0': Priority.P0,
            'P1': Priority.P1,
            'P2': Priority.P2,
            'P3': Priority.P3
        }
        return priority_map.get(priority_str.upper(), Priority.P1)
    
    def get_all_cases(self) -> List[TestCase]:
        """获取所有测试用例"""
        return self.test_cases
    
    def get_ui_cases(self) -> List[TestCase]:
        """获取用于 UI 测试的用例"""
        return [
            tc for tc in self.test_cases
            if tc.type in [TestType.FUNCTIONAL, TestType.UI, TestType.SMOKE]
        ]
    
    def get_summary(self) -> Dict:
        """获取统计摘要"""
        return {
            'total': len(self.test_cases),
            'by_priority': {
                p.value: len([c for c in self.test_cases if c.priority == p])
                for p in Priority
            },
            'by_type': {
                t.value: len([c for c in self.test_cases if c.type == t])
                for t in TestType
            },
            'by_module': self._group_by_module()
        }
    
    def _group_by_module(self) -> Dict[str, int]:
        """按模块分组统计"""
        modules = {}
        for tc in self.test_cases:
            modules[tc.module] = modules.get(tc.module, 0) + 1
        return modules


# 便捷函数
def parse_test_plan(plan_path: str, module_name: str = None) -> str:
    """
    读取测试计划文件
    
    Args:
        plan_path: 测试计划文件路径
        module_name: 模块名称（如果为空，从文件名推断）
    
    Returns:
        测试计划内容
    """
    path = Path(plan_path)
    if not path.exists():
        raise FileNotFoundError(f"测试计划文件不存在: {plan_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_test_cases(
    plan_content: str,
    module_name: str,
    url: str = "",
    mode: str = "all"
) -> List[TestCase]:
    """
    从测试计划生成测试用例
    
    Args:
        plan_content: 测试计划内容
        module_name: 模块名称
        url: 测试页面 URL
        mode: 生成模式 - "ui" 只生成 UI 测试，"all" 生成全部
    
    Returns:
        测试用例列表
    """
    config = {
        'ui_only': mode == 'ui',
        'include_negative': mode == 'all',
        'include_boundary': mode == 'all'
    }
    
    generator = TestCaseGenerator(config)
    return generator.generate_from_plan(plan_content, module_name, url)

