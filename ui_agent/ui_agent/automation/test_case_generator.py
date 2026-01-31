"""
自动化测试用例生成器

功能：输入 URL → 自动生成完整的 Playwright Java 测试用例

技术栈：
1. Playwright MCP - 分析页面交互场景
2. OpenAI GPT - 理解业务逻辑和生成测试用例
3. AI Skills - 场景识别和测试策略
"""

import asyncio
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path
from datetime import datetime

from ui_agent.llm import resolve_openai_config, create_openai_client


@dataclass
class TestScenario:
    """测试场景"""
    scenario_name: str  # 场景名称，如 "Create Printer Setting"
    test_method_name: str  # 测试方法名，如 "checkCreatePrinterSetting"
    description: str  # 场景描述
    priority: str  # P0/P1/P2/P3
    test_type: str  # smoke/regression/integration
    preconditions: List[str]  # 前置条件
    test_steps: List[str]  # 测试步骤
    expected_results: List[str]  # 预期结果
    assertions: List[str]  # 断言语句
    test_data: Dict[str, Any]  # 测试数据


@dataclass
class HelperMethod:
    """Helper 方法"""
    method_name: str  # 方法名
    parameters: List[str]  # 参数列表
    description: str  # 方法描述
    implementation: str  # 方法实现代码


@dataclass
class TestSuite:
    """测试套件"""
    page_url: str
    page_title: str
    test_class_name: str  # 测试类名，如 DeviceInventoryPageTest
    package_name: str
    page_object_class: str  # Page Object 类名
    helper_class_name: str  # Helper 类名
    scenarios: List[TestScenario]  # 测试场景列表
    helper_methods: List[HelperMethod]  # Helper 方法列表
    imports: List[str]  # 导入语句
    timestamp: str


class TestCaseGenerator:
    """
    测试用例生成器
    
    整合 Playwright MCP + OpenAI 分析页面场景并生成测试用例
    """
    
    def __init__(self, openai_api_key: str = None, model: Optional[str] = None, base_url: str = None):
        """
        Args:
            openai_api_key: OpenAI API Key
            model: Model name
            base_url: OpenAI API Base URL (optional)
        """
        resolved_model, resolved_api_key, resolved_base_url = resolve_openai_config(
            model=model,
            api_key=openai_api_key,
            base_url=base_url,
        )
        self.api_key = resolved_api_key
        self.model = resolved_model
        self.base_url = resolved_base_url
        self.client = create_openai_client(
            api_key=self.api_key,
            base_url=self.base_url,
        )

    async def generate_test_suite(
        self,
        url: str,
        auth_state: Optional[str] = None,
        reference_test: Optional[str] = None,
        page_object_class: Optional[str] = None,
        page_info: Optional[Dict[str, Any]] = None
    ) -> TestSuite:
        """
        生成完整测试套件
        
        Args:
            url: 页面 URL
            auth_state: 认证状态文件
            reference_test: 参考测试用例代码
            page_object_class: Page Object 类代码
        
        Returns:
            TestSuite: 完整的测试套件
        """
        print("🚀 开始生成测试套件...")
        
        # 1. 使用 Playwright 访问页面并提取交互信息
        if page_info is None:
            page_info = await self._analyze_page_interactions(url, auth_state)
        
        # 2. 使用 AI 分析业务场景和生成测试用例
        test_suite = await self._generate_test_scenarios(
            page_info, 
            url, 
            reference_test,
            page_object_class
        )
        
        return test_suite
    
    async def _analyze_page_interactions(
        self,
        url: str,
        auth_state: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        使用 Playwright 分析页面交互
        
        提取：
        1. 页面元素（按钮、输入框、表格等）
        2. 可执行操作（点击、输入、选择等）
        3. 表单结构
        4. 导航流程
        """
        print("🔍 分析页面交互...")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("⚠️  需要安装 Playwright: pip install playwright")
            return {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            context_options = {}
            if auth_state and Path(auth_state).exists():
                context_options['storage_state'] = auth_state
            
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            try:
                await page.goto(url, wait_until='load', timeout=90000)
                await page.wait_for_timeout(5000)
                
                # 提取页面信息
                page_info = {
                    'url': url,
                    'title': await page.title(),
                    'html': await page.content(),
                    'buttons': await self._extract_buttons(page),
                    'inputs': await self._extract_inputs(page),
                    'forms': await self._extract_forms(page),
                    'tables': await self._extract_tables(page),
                    'links': await self._extract_navigation(page)
                }
                
                print(f"📊 页面分析完成:")
                print(f"   - 按钮: {len(page_info['buttons'])} 个")
                print(f"   - 输入框: {len(page_info['inputs'])} 个")
                print(f"   - 表单: {len(page_info['forms'])} 个")
                print(f"   - 表格: {len(page_info['tables'])} 个")
                
                return page_info
                
            finally:
                await context.close()
                await browser.close()
    
    async def _extract_buttons(self, page) -> List[Dict]:
        """提取所有按钮"""
        buttons = []
        try:
            button_elements = await page.locator('button, [role="button"], input[type="button"], input[type="submit"]').all()
            for btn in button_elements[:20]:  # 限制数量
                text = await btn.text_content() or await btn.get_attribute('aria-label') or ''
                if text.strip():
                    buttons.append({
                        'text': text.strip(),
                        'type': await btn.get_attribute('type') or 'button'
                    })
        except:
            pass
        return buttons
    
    async def _extract_inputs(self, page) -> List[Dict]:
        """提取所有输入框"""
        inputs = []
        try:
            input_elements = await page.locator('input, textarea, select').all()
            for inp in input_elements[:30]:  # 限制数量
                name = await inp.get_attribute('name') or ''
                input_type = await inp.get_attribute('type') or 'text'
                placeholder = await inp.get_attribute('placeholder') or ''
                
                inputs.append({
                    'name': name,
                    'type': input_type,
                    'placeholder': placeholder,
                    'label': await self._find_label_for_input(page, name)
                })
        except:
            pass
        return inputs
    
    async def _extract_forms(self, page) -> List[Dict]:
        """提取表单结构"""
        forms = []
        try:
            form_elements = await page.locator('form').all()
            for form in form_elements:
                form_inputs = await form.locator('input, textarea, select').all()
                forms.append({
                    'input_count': len(form_inputs),
                    'has_submit': len(await form.locator('[type="submit"], button[type="submit"]').all()) > 0
                })
        except:
            pass
        return forms
    
    async def _extract_tables(self, page) -> List[Dict]:
        """提取表格信息"""
        tables = []
        try:
            table_elements = await page.locator('table, [role="table"]').all()
            for table in table_elements:
                headers = await table.locator('th, [role="columnheader"]').all()
                rows = await table.locator('tr, [role="row"]').all()
                
                tables.append({
                    'columns': len(headers),
                    'rows': len(rows)
                })
        except:
            pass
        return tables
    
    async def _extract_navigation(self, page) -> List[str]:
        """提取导航链接"""
        links = []
        try:
            link_elements = await page.locator('a[href]').all()
            for link in link_elements[:20]:
                text = await link.text_content()
                if text and text.strip():
                    links.append(text.strip())
        except:
            pass
        return links
    
    async def _find_label_for_input(self, page, input_name: str) -> str:
        """查找输入框对应的 label"""
        try:
            if not input_name:
                return ""
            label = await page.locator(f'label[for="{input_name}"]').first.text_content()
            return label or ""
        except:
            return ""
    
    async def _generate_test_scenarios(
        self,
        page_info: Dict,
        url: str,
        reference_test: Optional[str] = None,
        page_object_class: Optional[str] = None
    ) -> TestSuite:
        """
        使用 AI 生成测试场景
        """
        print("🤖 AI 正在生成测试场景...")
        
        if not self.client:
            print("❌ OpenAI 客户端未初始化")
            return None
        
        # 构建提示词
        prompt = self._create_test_generation_prompt(page_info, url, reference_test, page_object_class)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的测试工程师，擅长编写 Playwright Java 自动化测试用例。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result_text = response.choices[0].message.content
            print(f"✅ AI 分析完成，返回 {len(result_text)} 字符")
            
            # 解析 JSON
            test_suite = self._parse_test_suite_json(result_text, url)
            
            return test_suite
            
        except Exception as e:
            print(f"❌ AI 生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _create_test_generation_prompt(
        self,
        page_info: Dict,
        url: str,
        reference_test: Optional[str] = None,
        page_object_class: Optional[str] = None
    ) -> str:
        """创建测试生成提示词"""
        
        prompt = f"""
请为以下网页生成完整的 Playwright Java 测试用例。

## 页面信息
URL: {page_info['url']}
标题: {page_info['title']}

## 页面元素分析
按钮数量: {len(page_info.get('buttons', []))}
输入框数量: {len(page_info.get('inputs', []))}
表单数量: {len(page_info.get('forms', []))}
表格数量: {len(page_info.get('tables', []))}

### 主要按钮:
{self._format_buttons(page_info.get('buttons', []))}

### 主要输入框:
{self._format_inputs(page_info.get('inputs', []))}

## 测试用例生成要求

### 1. 测试场景识别
基于页面元素，识别以下类型的测试场景：
- **CRUD 操作**: Create (创建), Read (查询), Update (更新), Delete (删除)
- **表单验证**: 必填字段、格式校验、边界值测试
- **搜索功能**: 有结果搜索、无结果搜索、模糊搜索
- **表格操作**: 排序、筛选、分页
- **导航测试**: 页面跳转、返回、关闭

### 2. 测试方法命名规范
- 使用 camelCase
- 前缀: check/verify/test
- 描述性：checkCreatePrinterSetting, verifySearchWithNoResults

### 3. 测试数据生成
- 随机字符串: CommonMethod.generateRandomString(8)
- 唯一名称: "prefix_" + CommonMethod.generateRandomString(8)

### 4. Helper 方法设计
为每个复杂操作创建 Helper 方法：
```java
// 导航到页面
public void goToXXXPage() {{
    page.navigate(url);
}}

// 创建操作
public void createXXX(String name, String description) {{
    xxxPage.nameInput.fill(name);
    xxxPage.descriptionInput.fill(description);
    xxxPage.saveButton.click();
}}

// 验证操作
public void assertXXXCreated(String name) {{
    String actual = xxxPage.nameValue.textContent();
    assertEquals(name, actual);
}}
```

### 5. 测试用例结构
```java
@Test
@Tag("smoke")
void testMethodName() throws Exception {{
    // 1. 导航到页面
    commonHelper.goToXXXPage();
    
    // 2. 准备测试数据
    String expectedName = "prefix_" + CommonMethod.generateRandomString(8);
    
    // 3. 执行操作
    xxxHelper.createXXX(expectedName, description);
    
    // 4. 验证结果
    xxxHelper.assertXXXCreated(expectedName);
}}
```

## 输出格式（必须严格遵守 JSON 格式）

返回 JSON 对象，包含以下字段：
{{
  "test_class_name": "DeviceInventoryPageTest",
  "package_name": "com.zebra.TestCase.smokeTest",
  "page_object_class": "DeviceInventoryPage",
  "helper_class_name": "DeviceInventoryHelper",
  "imports": [
    "com.zebra.helper.Hook",
    "org.junit.jupiter.api.Test",
    "static org.junit.jupiter.api.Assertions.assertEquals"
  ],
  "scenarios": [
    {{
      "scenario_name": "Create Device",
      "test_method_name": "checkCreateDevice",
      "description": "验证创建设备功能",
      "priority": "P0",
      "test_type": "smoke",
      "preconditions": [
        "用户已登录",
        "有权限创建设备"
      ],
      "test_steps": [
        "导航到设备清单页面",
        "点击创建按钮",
        "填写设备名称",
        "点击保存按钮"
      ],
      "expected_results": [
        "设备创建成功",
        "列表中显示新设备"
      ],
      "assertions": [
        "assertEquals(expectedName, actualName)"
      ],
      "test_data": {{
        "deviceName": "\"device_\" + CommonMethod.generateRandomString(8)"
      }}
    }}
  ],
  "helper_methods": [
    {{
      "method_name": "goToDeviceInventoryPage",
      "parameters": [],
      "description": "导航到设备清单页面",
      "implementation": "page.navigate(\\"https://harmonix-dev.zebra.com/all/devices\\");"
    }},
    {{
      "method_name": "createDevice",
      "parameters": ["String deviceName"],
      "description": "创建设备",
      "implementation": "deviceInventoryPage.createButton.click();\\ndeviceInventoryPage.nameInput.fill(deviceName);\\ndeviceInventoryPage.saveButton.click();"
    }}
  ]
}}
"""
        
        # 添加参考测试用例
        if reference_test:
            prompt += f"""

## 参考测试用例（请模仿这个风格）
```java
{reference_test[:3000]}
```
"""
        
        # 添加 Page Object 类
        if page_object_class:
            prompt += f"""

## Page Object 类（使用这些元素定位器）
```java
{page_object_class[:2000]}
```
"""
        
        prompt += "\n\n请严格按照 JSON 格式返回，不要包含任何其他文本。"
        
        return prompt
    
    def _format_buttons(self, buttons: List[Dict]) -> str:
        """格式化按钮列表"""
        if not buttons:
            return "无"
        return "\n".join([f"- {btn.get('text', '')} ({btn.get('type', 'button')})" for btn in buttons[:10]])
    
    def _format_inputs(self, inputs: List[Dict]) -> str:
        """格式化输入框列表"""
        if not inputs:
            return "无"
        return "\n".join([
            f"- {inp.get('name', 'unnamed')} ({inp.get('type', 'text')}): {inp.get('label', '') or inp.get('placeholder', '')}"
            for inp in inputs[:10]
        ])
    
    def _parse_test_suite_json(self, json_str: str, url: str) -> TestSuite:
        """解析 JSON 生成 TestSuite 对象"""
        try:
            data = json.loads(json_str)
            
            # 解析测试场景
            scenarios = []
            for scenario_data in data.get('scenarios', []):
                scenario = TestScenario(
                    scenario_name=scenario_data.get('scenario_name', ''),
                    test_method_name=scenario_data.get('test_method_name', ''),
                    description=scenario_data.get('description', ''),
                    priority=scenario_data.get('priority', 'P2'),
                    test_type=scenario_data.get('test_type', 'smoke'),
                    preconditions=scenario_data.get('preconditions', []),
                    test_steps=scenario_data.get('test_steps', []),
                    expected_results=scenario_data.get('expected_results', []),
                    assertions=scenario_data.get('assertions', []),
                    test_data=scenario_data.get('test_data', {})
                )
                scenarios.append(scenario)
            
            # 解析 Helper 方法
            helper_methods = []
            for method_data in data.get('helper_methods', []):
                helper_method = HelperMethod(
                    method_name=method_data.get('method_name', ''),
                    parameters=method_data.get('parameters', []),
                    description=method_data.get('description', ''),
                    implementation=method_data.get('implementation', '')
                )
                helper_methods.append(helper_method)
            
            # 构建 TestSuite
            test_suite = TestSuite(
                page_url=url,
                page_title=data.get('page_title', ''),
                test_class_name=data.get('test_class_name', ''),
                package_name=data.get('package_name', 'com.zebra.TestCase.smokeTest'),
                page_object_class=data.get('page_object_class', ''),
                helper_class_name=data.get('helper_class_name', ''),
                scenarios=scenarios,
                helper_methods=helper_methods,
                imports=data.get('imports', []),
                timestamp=datetime.now().isoformat()
            )
            
            return test_suite
            
        except Exception as e:
            print(f"❌ JSON 解析失败: {e}")
            print(f"原始 JSON:\n{json_str[:500]}")
            return None
    
    def generate_test_class_code(self, test_suite: TestSuite) -> str:
        """
        生成测试类 Java 代码
        """
        lines = []
        
        # Package
        lines.append(f"package {test_suite.package_name};")
        lines.append("")
        
        # Imports
        default_imports = [
            "com.epam.reportportal.junit5.ReportPortalExtension",
            "com.zebra.common.CommonMethod",
            "com.zebra.helper.Hook",
            "com.zebra.property.HarmonixProperty",
            "org.junit.jupiter.api.*",
            "org.junit.jupiter.api.extension.ExtendWith",
            "static org.junit.jupiter.api.Assertions.*"
        ]
        
        all_imports = list(set(default_imports + test_suite.imports))
        for imp in sorted(all_imports):
            lines.append(f"import {imp};")
        
        lines.append("")
        
        # 类注释
        lines.append("/**")
        lines.append(f" * {test_suite.test_class_name}")
        lines.append(f" * 页面: {test_suite.page_url}")
        lines.append(f" * ")
        lines.append(f" * 自动生成时间: {test_suite.timestamp}")
        lines.append(f" * 模型: {self.model}")
        lines.append(" */")
        
        # 类定义
        lines.append("@ExtendWith(ReportPortalExtension.class)")
        lines.append(f"public class {test_suite.test_class_name} extends Hook {{")
        lines.append("")
        
        # BeforeAll
        page_name = test_suite.test_class_name.replace("Test", "")
        lines.append("    @BeforeAll")
        lines.append("    static void skipIfSkipModule() {")
        lines.append("        Assumptions.assumeFalse(")
        lines.append(f"                HarmonixProperty.skipModule.contains(\"{page_name}\".toLowerCase()),")
        lines.append("                \"Tests are skipped in this environment\"")
        lines.append("        );")
        lines.append("    }")
        lines.append("")
        
        # 测试方法
        for scenario in test_suite.scenarios:
            lines.extend(self._generate_test_method(scenario))
            lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_test_method(self, scenario: TestScenario) -> List[str]:
        """生成单个测试方法"""
        lines = []
        
        # JavaDoc 注释
        lines.append("    /**")
        lines.append(f"     * {scenario.description}")
        lines.append("     * ")
        lines.append("     * 前置条件:")
        for pre in scenario.preconditions:
            lines.append(f"     * - {pre}")
        lines.append("     * ")
        lines.append("     * 测试步骤:")
        for i, step in enumerate(scenario.test_steps, 1):
            lines.append(f"     * {i}. {step}")
        lines.append("     * ")
        lines.append("     * 预期结果:")
        for result in scenario.expected_results:
            lines.append(f"     * - {result}")
        lines.append("     */")
        
        # 方法签名
        lines.append("    @Test")
        lines.append(f"    @Tag(\"{scenario.test_type}\")")
        lines.append(f"    void {scenario.test_method_name}() throws Exception {{")
        
        # 方法体（需要根据具体场景生成）
        lines.append("        // TODO: 根据测试步骤实现测试逻辑")
        lines.append("        ")
        
        # 测试数据
        for data_name, data_value in scenario.test_data.items():
            lines.append(f"        String {data_name} = {data_value};")
        
        lines.append("        ")
        
        # 测试步骤（简化版本）
        for step in scenario.test_steps[:3]:  # 只生成前3步作为示例
            lines.append(f"        // {step}")
        
        lines.append("        ")
        
        # 断言
        for assertion in scenario.assertions:
            lines.append(f"        {assertion};")
        
        lines.append("    }")
        
        return lines
    
    def generate_helper_class_code(self, test_suite: TestSuite) -> str:
        """
        生成 Helper 类 Java 代码
        """
        lines = []
        
        # Package
        lines.append("package com.zebra.helper;")
        lines.append("")
        
        # Imports
        lines.append("import com.microsoft.playwright.Page;")
        lines.append(f"import com.zebra.pageobject.{test_suite.page_object_class};")
        lines.append("import static org.junit.jupiter.api.Assertions.*;")
        lines.append("")
        
        # 类定义
        lines.append("/**")
        lines.append(f" * {test_suite.helper_class_name}")
        lines.append(f" * 为 {test_suite.page_object_class} 提供辅助方法")
        lines.append(" */")
        lines.append(f"public class {test_suite.helper_class_name} {{")
        lines.append("")
        
        # 字段
        lines.append("    private final Page page;")
        lines.append(f"    private final {test_suite.page_object_class} {self._to_camel_case(test_suite.page_object_class)};")
        lines.append("")
        
        # 构造函数
        lines.append(f"    public {test_suite.helper_class_name}(Page page) {{")
        lines.append("        this.page = page;")
        lines.append(f"        this.{self._to_camel_case(test_suite.page_object_class)} = new {test_suite.page_object_class}(page);")
        lines.append("    }")
        lines.append("")
        
        # Helper 方法
        for method in test_suite.helper_methods:
            lines.extend(self._generate_helper_method(method))
            lines.append("")
        
        lines.append("}")
        
        return "\n".join(lines)
    
    def _generate_helper_method(self, method: HelperMethod) -> List[str]:
        """生成 Helper 方法"""
        lines = []
        
        # 方法注释
        lines.append("    /**")
        lines.append(f"     * {method.description}")
        lines.append("     */")
        
        # 方法签名
        params_str = ", ".join(method.parameters) if method.parameters else ""
        lines.append(f"    public void {method.method_name}({params_str}) {{")
        
        # 方法实现
        impl_lines = method.implementation.split("\\n")
        for impl_line in impl_lines:
            lines.append(f"        {impl_line}")
        
        lines.append("    }")
        
        return lines
    
    def _to_camel_case(self, text: str) -> str:
        """转换为 camelCase"""
        if not text:
            return text
        return text[0].lower() + text[1:]
    
    def save_to_files(self, test_suite: TestSuite, output_dir: str) -> Dict[str, str]:
        """
        保存测试类和 Helper 类到文件
        
        Returns:
            Dict: {'test_class': path, 'helper_class': path, 'json': path}
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        files = {}
        
        # 生成并保存测试类
        test_code = self.generate_test_class_code(test_suite)
        test_file = output_path / f"{test_suite.test_class_name}.java"
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_code)
        files['test_class'] = str(test_file)
        print(f"✅ 测试类已保存: {test_file}")
        
        # 生成并保存 Helper 类
        helper_code = self.generate_helper_class_code(test_suite)
        helper_file = output_path / f"{test_suite.helper_class_name}.java"
        with open(helper_file, 'w', encoding='utf-8') as f:
            f.write(helper_code)
        files['helper_class'] = str(helper_file)
        print(f"✅ Helper 类已保存: {helper_file}")
        
        # 保存 JSON 数据
        json_data = {
            'test_suite': asdict(test_suite),
            'generation_time': test_suite.timestamp,
            'model': self.model
        }
        json_file = output_path / 'test_suite.json'
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        files['json'] = str(json_file)
        print(f"✅ JSON 数据已保存: {json_file}")
        
        return files
