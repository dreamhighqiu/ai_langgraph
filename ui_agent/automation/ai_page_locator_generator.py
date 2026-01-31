"""
AI 增强的页面定位器生成器

使用 Browser-Use + LLM 分析页面元素
生成符合项目规范的 Java Page Object 代码

特点：
1. AI 理解元素业务语义
2. 智能命名字段
3. 自动分组（Wi-Fi、Bluetooth等）
4. 生成符合现有代码风格的定位器
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
class AIElementInfo:
    """AI 识别的元素信息"""
    field_name: str  # 语义化的字段名，如 ssidInput, nextButton
    locator_code: str  # Playwright Java 定位器代码
    element_type: str  # button, input, radio, select, etc.
    description: str  # 元素用途描述
    group: str  # 所属分组，如 "Wi-Fi Setup", "Bluetooth Setup"
    confidence: float = 1.0  # AI 识别置信度
    alternative_locators: List[str] = field(default_factory=list)  # 备选定位器


@dataclass
class AIPageAnalysis:
    """AI 页面分析结果"""
    page_url: str
    page_title: str
    class_name: str
    package_name: str
    timestamp: str
    element_groups: Dict[str, List[AIElementInfo]] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
    helper_methods: List[str] = field(default_factory=list)


class AIPageLocatorGenerator:
    """
    AI 增强的页面定位器生成器
    
    使用 LLM 分析页面元素，生成高质量的 Page Object 代码
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

    async def analyze_page_with_browser_use(
        self, 
        url: str, 
        auth_state: Optional[str] = None,
        reference_code: Optional[str] = None
    ) -> AIPageAnalysis:
        """
        使用 Playwright + OpenAI 分析页面
        
        Args:
            url: 页面地址
            auth_state: 认证状态文件
            reference_code: 参考代码（现有的 Page Object 类）
        
        Returns:
            AIPageAnalysis: 分析结果
        """
        print("🤖 使用 Playwright + OpenAI 分析页面...")
        
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            print("⚠️  需要安装 Playwright: pip install playwright")
            return None
        
        # 使用 Playwright 访问页面并获取 HTML
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            
            # 加载认证状态
            context_options = {}
            if auth_state and Path(auth_state).exists():
                context_options['storage_state'] = auth_state
                print(f"📋 已加载认证状态: {auth_state}")
            
            context = await browser.new_context(**context_options)
            page = await context.new_page()
            
            try:
                print(f"🌐 访问页面: {url}")
                # 使用 load 而不是 networkidle，更宽松的等待策略
                await page.goto(url, wait_until='load', timeout=90000)
                
                # 等待页面稳定
                print("⏳ 等待页面加载...")
                await page.wait_for_timeout(5000)
                
                # 等待常见的内容加载
                try:
                    await page.wait_for_selector('body', state='visible', timeout=10000)
                except:
                    print("⚠️  未检测到 body 元素，继续...")
                
                # 获取页面 HTML 和标题
                html_content = await page.content()
                page_title = await page.title()
                
                print(f"📄 页面标题: {page_title}")
                print(f"📏 HTML 长度: {len(html_content)} 字符")
                
            finally:
                await context.close()
                await browser.close()
        
        # 使用 OpenAI 分析 HTML
        print("🤖 AI 正在分析 HTML 内容...")
        analysis = await self._analyze_html_with_openai(
            html_content=html_content,
            page_url=url,
            page_title=page_title,
            reference_code=reference_code
        )
        
        return analysis
    
    async def _analyze_html_with_openai(
        self,
        html_content: str,
        page_url: str,
        page_title: str,
        reference_code: Optional[str] = None
    ) -> AIPageAnalysis:
        """使用 OpenAI 分析 HTML 内容"""
        
        if not self.client:
            print("❌ OpenAI 客户端未初始化")
            return None
        
        # 清理 HTML（移除 script 和 style 标签）
        cleaned_html = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        cleaned_html = re.sub(r'<style[^>]*>.*?</style>', '', cleaned_html, flags=re.DOTALL)
        
        # 限制 HTML 长度（避免超过 token 限制）
        max_html_len = 50000
        if len(cleaned_html) > max_html_len:
            cleaned_html = cleaned_html[:max_html_len] + "\n\n... (HTML 内容已截断)"
        
        # 创建提示词
        prompt = self._create_html_analysis_prompt(page_url, cleaned_html, reference_code)
        
        try:
            # 调用 OpenAI API
            print(f"📡 请求 OpenAI API: {self.model}")
            print(f"   Base URL: {self.base_url or 'https://api.openai.com/v1'}")
            print(f"   Timeout: 120s, Max retries: 2")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的测试自动化工程师，擅长分析网页并生成 Playwright Java Page Object 代码。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_format={"type": "json_object"}
            )
            
            # 解析响应
            result_text = response.choices[0].message.content
            print(f"✅ AI 分析完成，返回 {len(result_text)} 字符")
            
            # 解析 JSON
            analysis = self._parse_ai_result(result_text, page_url)
            if analysis:
                analysis.page_title = page_title
            
            return analysis
            
        except Exception as e:
            print(f"\n❌ OpenAI API 调用失败: {e}")
            print(f"\n🔍 网络诊断:")
            print(f"   1. 检查网络连接: ping api.openai.com")
            print(f"   2. 检查防火墙设置")
            print(f"   3. 如需要代理，设置环境变量:")
            print(f"      set HTTP_PROXY=http://proxy.company.com:8080")
            print(f"      set HTTPS_PROXY=http://proxy.company.com:8080")
            print(f"   4. 验证 API Key 是否有效")
            print(f"   5. 检查 base_url 是否正确: {self.base_url}")
            
            import traceback
            traceback.print_exc()
            return None
    
    def _create_html_analysis_prompt(self, url: str, html_content: str, reference_code: Optional[str] = None) -> str:
        """创建 HTML 分析提示词"""
        
        prompt = f"""
请分析以下 HTML 页面并提取所有可交互元素。

页面 URL: {url}

HTML 内容:
```html
{html_content}
```

任务要求：
1. 识别所有可交互元素（按钮、输入框、单选按钮、下拉框、链接等）
2. 为每个元素提供：
   - 语义化的 camelCase 字段名（如 ssidInput, nextButton, securityTypeOpen）
   - Playwright Java 定位器代码（优先使用 getByRole, getByText, locator 等）
   - 元素类型（button/input/radio/select/link）
   - 元素用途描述
3. 将元素按功能分组（如 "Wi-Fi Setup", "Bluetooth Setup", "Basic Properties", "Navigation"）

重要定位器规则：
- 优先使用 page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("按钮文本"))
- 对于自定义组件（如 zeta-radio-button），使用 page.locator("zeta-radio-button:has-text('文本')")
- 对于 name 属性明确的输入框，使用 page.locator("input[name='字段名']")
- 单选按钮组要拆分为独立的字段，每个选项一个字段

字段命名规范：
- 按钮：xxxButton（如 nextButton, saveButton）
- 输入框：xxxInput（如 ssidInput, passwordInput）
- 单选按钮：前缀+选项（如 securityTypeOpen, bluetoothRadioEnabled）
- 下拉框：xxxSelect 或 xxxDropdown

必须返回 JSON 格式（不要包含任何其他文本）：
{{
  "page_title": "页面标题",
  "element_groups": {{
    "Wi-Fi Setup": [
      {{
        "field_name": "ssidInput",
        "locator_code": "page.locator(\\"input[name='wifiConfig.ssid']\\")",
        "element_type": "input",
        "description": "SSID/网络名称输入框"
      }}
    ]
  }},
  "helper_methods": []
}}
"""
        
        # 如果提供了参考代码，添加到提示中
        if reference_code:
            prompt += f"""

参考代码风格（请严格模仿）：
```java
{reference_code[:2000]}
```

请严格按照参考代码的命名和定位器风格生成。
"""
        
        return prompt
    
    def _create_analysis_prompt(self, url: str, reference_code: Optional[str] = None) -> str:
        """创建 AI 分析提示词"""
        
        prompt = f"""
请访问页面 {url} 并分析所有可交互元素。

任务要求：
1. 识别所有可交互元素（按钮、输入框、单选按钮、下拉框、链接等）
2. 为每个元素提供：
   - 语义化的 camelCase 字段名（如 ssidInput, nextButton, securityTypeOpen）
   - Playwright Java 定位器代码（优先使用 getByRole, getByText, locator 等）
   - 元素类型（button/input/radio/select/link）
   - 元素用途描述
3. 将元素按功能分组（如 "Wi-Fi Setup", "Bluetooth Setup", "Basic Properties", "Navigation"）

重要定位器规则：
- 优先使用 page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("按钮文本"))
- 对于自定义组件（如 zeta-radio-button），使用 page.locator("zeta-radio-button:has-text('文本')")
- 对于 name 属性明确的输入框，使用 page.locator("input[name='字段名']")
- 单选按钮组要拆分为独立的字段，每个选项一个字段

字段命名规范：
- 按钮：xxxButton（如 nextButton, saveButton）
- 输入框：xxxInput（如 ssidInput, passwordInput）
- 单选按钮：前缀+选项（如 securityTypeOpen, bluetoothRadioEnabled）
- 下拉框：xxxSelect 或 xxxDropdown
- 步骤导航：xxxStep（如 connectivityStep）

返回 JSON 格式：
{{
  "page_title": "页面标题",
  "element_groups": {{
    "Wi-Fi Setup": [
      {{
        "field_name": "ssidInput",
        "locator_code": "page.locator(\\"input[name='wifiConfig.ssid']\\")",
        "element_type": "input",
        "description": "SSID/网络名称输入框"
      }},
      {{
        "field_name": "securityTypeOpen",
        "locator_code": "page.locator(\\"zeta-radio-button:has-text('Open')\\")",
        "element_type": "radio",
        "description": "Wi-Fi 安全类型 - 开放"
      }},
      {{
        "field_name": "securityTypePersonal",
        "locator_code": "page.locator(\\"zeta-radio-button:has-text('Personal')\\")",
        "element_type": "radio",
        "description": "Wi-Fi 安全类型 - 个人"
      }}
    ],
    "Navigation": [
      {{
        "field_name": "nextButton",
        "locator_code": "page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName(\\"Next chevron_right\\"))",
        "element_type": "button",
        "description": "下一步按钮"
      }}
    ]
  }},
  "helper_methods": [
    "getRfBandSelectOption",
    "getWpaModeOption"
  ]
}}
"""
        
        # 如果提供了参考代码，添加到提示中
        if reference_code:
            prompt += f"""

参考代码风格（请模仿这个风格）：
```java
{reference_code[:2000]}  // 只取前2000字符
```

请严格按照参考代码的命名和定位器风格生成。
"""
        
        return prompt
    
    def _parse_ai_result(self, result: str, url: str) -> AIPageAnalysis:
        """解析 AI 返回的结果"""
        
        try:
            # 提取 JSON（AI 可能返回包含解释的文本）
            json_match = re.search(r'\{.*\}', result, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group())
            else:
                raise ValueError("无法从 AI 响应中提取 JSON")
            
            # 构建分析结果
            analysis = AIPageAnalysis(
                page_url=url,
                page_title=data.get('page_title', 'Unknown Page'),
                class_name=self._generate_class_name(data.get('page_title', 'Page')),
                package_name="com.zebra.pageobject",
                timestamp=datetime.now().isoformat()
            )
            
            # 解析元素分组
            for group_name, elements in data.get('element_groups', {}).items():
                element_list = []
                for elem_data in elements:
                    element = AIElementInfo(
                        field_name=elem_data.get('field_name', 'unknownElement'),
                        locator_code=elem_data.get('locator_code', ''),
                        element_type=elem_data.get('element_type', 'unknown'),
                        description=elem_data.get('description', ''),
                        group=group_name,
                        confidence=elem_data.get('confidence', 1.0),
                        alternative_locators=elem_data.get('alternative_locators', [])
                    )
                    element_list.append(element)
                
                analysis.element_groups[group_name] = element_list
            
            # 添加导入
            analysis.imports = [
                "import com.microsoft.playwright.Locator;",
                "import com.microsoft.playwright.Page;",
                "import com.microsoft.playwright.options.AriaRole;",
                "import com.zebra.pageobject.CommonPage;",
            ]
            
            # 检查是否需要 Pattern
            all_locators = ' '.join([e.locator_code for group in analysis.element_groups.values() for e in group])
            if 'Pattern.compile' in all_locators:
                analysis.imports.append("import java.util.regex.Pattern;")
            
            # 添加辅助方法
            analysis.helper_methods = data.get('helper_methods', [])
            
            return analysis
            
        except Exception as e:
            print(f"❌ 解析 AI 结果失败: {e}")
            print(f"原始结果:\n{result}")
            return None
    
    def _generate_class_name(self, page_title: str) -> str:
        """从页面标题生成类名"""
        clean = re.sub(r'[^\w\s]', '', page_title)
        parts = clean.split()
        class_name = ''.join(word.capitalize() for word in parts if word)
        
        if not class_name.endswith('Page'):
            class_name += 'Page'
        
        return class_name or 'GeneratedPage'
    
    def generate_java_code(self, analysis: AIPageAnalysis) -> str:
        """生成 Java Page Object 代码"""
        
        lines = []
        
        # Package
        lines.append(f"package {analysis.package_name};")
        lines.append("")
        
        # Imports
        for imp in analysis.imports:
            lines.append(imp)
        lines.append("")
        
        # 类注释
        lines.append("/**")
        lines.append(f" * {analysis.page_title}")
        lines.append(f" * 页面URL: {analysis.page_url}")
        lines.append(f" * ")
        lines.append(f" * 由 AI 增强的 PageLocatorGenerator 自动生成")
        lines.append(f" * 生成时间: {analysis.timestamp}")
        lines.append(f" * 模型: {self.model}")
        lines.append(" */")
        
        # 类定义
        lines.append(f"public class {analysis.class_name} extends CommonPage {{")
        lines.append("")
        
        # 字段定义（按分组）
        for group_name, elements in analysis.element_groups.items():
            if not elements:
                continue
            
            lines.append(f"    // {group_name}")
            for elem in elements:
                # 字段注释
                if elem.description:
                    lines.append(f"    /** {elem.description} */")
                lines.append(f"    public final Locator {elem.field_name};")
            lines.append("")
        
        # 构造函数
        lines.append("    /**")
        lines.append("     * 构造函数")
        lines.append("     * @param page Playwright Page 对象")
        lines.append("     */")
        lines.append(f"    public {analysis.class_name}(Page page) {{")
        lines.append("        super(page);")
        lines.append("")
        
        # 初始化定位器（按分组）
        for group_name, elements in analysis.element_groups.items():
            if not elements:
                continue
            
            lines.append(f"        // {group_name}")
            for elem in elements:
                lines.append(f"        this.{elem.field_name} = {elem.locator_code};")
            lines.append("")
        
        lines.append("    }")
        
        # 辅助方法
        if analysis.helper_methods:
            lines.append("")
            lines.append("    // 辅助方法")
            for method_name in analysis.helper_methods:
                lines.append(f"    // TODO: 实现 {method_name}() 方法")
        
        # 类结束
        lines.append("}")
        lines.append("")
        
        return '\n'.join(lines)
    
    def save_to_file(self, analysis: AIPageAnalysis, output_dir: str) -> str:
        """保存生成的代码"""
        
        # 生成代码
        code = self.generate_java_code(analysis)
        
        # 确定输出路径
        output_path = Path(output_dir) / f"{analysis.class_name}.java"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(code)
        
        print(f"✅ Java Page Object 已保存: {output_path}")
        
        # 同时保存 JSON 分析结果
        json_path = Path(output_dir) / 'ai_analysis.json'
        with open(json_path, 'w', encoding='utf-8') as f:
            # 转换为可序列化的格式
            json_data = {
                'page_url': analysis.page_url,
                'page_title': analysis.page_title,
                'class_name': analysis.class_name,
                'package_name': analysis.package_name,
                'timestamp': analysis.timestamp,
                'element_groups': {
                    group: [asdict(elem) for elem in elements]
                    for group, elements in analysis.element_groups.items()
                }
            }
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 分析数据已保存: {json_path}")
        
        return str(output_path)
    
    async def analyze_with_vision(
        self,
        screenshot_path: str,
        url: str,
        reference_code: Optional[str] = None
    ) -> AIPageAnalysis:
        """
        使用 GPT-4 Vision 分析页面截图
        
        适用于无法直接访问页面的情况
        """
        if not self.client:
            print("❌ 需要配置 OpenAI API Key")
            return None
        
        print("🖼️  使用 Vision API 分析页面截图...")
        
        import base64
        
        # 读取截图
        with open(screenshot_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode('utf-8')
        
        # 创建提示
        prompt = f"""
这是一个网页的截图。请分析所有可交互元素并生成 Playwright Java Page Object 代码。

页面URL: {url}

要求：
1. 识别所有按钮、输入框、单选按钮、下拉框等可交互元素
2. 为每个元素提供语义化的字段名（camelCase）
3. 提供最佳的 Playwright 定位器策略
4. 按功能分组元素

返回 JSON 格式（与之前相同）。
"""
        
        if reference_code:
            prompt += f"\n\n参考代码风格：\n```java\n{reference_code[:1500]}\n```"
        
        # 调用 Vision API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }],
                max_tokens=4000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            analysis = self._parse_ai_result(result, url)
            
            return analysis
            
        except Exception as e:
            print(f"❌ Vision API 调用失败: {e}")
            return None


async def main():
    """测试函数"""
    import os
    
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL')
    if not api_key:
        print("请设置 OPENAI_API_KEY 环境变量")
        return
    if not model:
        print("请设置 OPENAI_MODEL 环境变量")
        return
    
    generator = AIPageLocatorGenerator(api_key, model=model)
    
    # 测试 URL
    url = "https://harmonix-dev.zebra.com/wizard/printers/stage/XXX?currentStep=Connectivity"
    
    # 读取参考代码
    reference_path = Path(__file__).parent.parent.parent / "pageobject" / "Printer" / "PrinterSetupProfile" / "CreatePrinterSetupPage.java"
    reference_code = None
    if reference_path.exists():
        with open(reference_path, 'r', encoding='utf-8') as f:
            reference_code = f.read()
    
    # 分析页面
    analysis = await generator.analyze_page_with_browser_use(
        url=url,
        reference_code=reference_code
    )
    
    if analysis:
        # 生成代码
        output_dir = "output/ai_generated"
        generator.save_to_file(analysis, output_dir)
        print("\n✅ 完成！")


if __name__ == '__main__':
    asyncio.run(main())
