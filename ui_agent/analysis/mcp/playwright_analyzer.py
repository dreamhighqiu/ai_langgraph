"""
MCP 模式 - Playwright 分析器
使用 Playwright MCP Server 进行网页分析

通过 MCP 协议，AI Agent 可以直接调用 Playwright 工具进行页面分析。
此模块作为 MCP 调用的桥接层，提供统一的分析接口。
"""

from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import asyncio
import json

from ...core.config import get_config
from ui_agent.mcp.registry import get_playwright_mcp_tools


@dataclass
class MCPAnalysisResult:
    """MCP 分析结果"""
    url: str
    title: str
    timestamp: str
    elements: Dict[str, List[Dict]] = field(default_factory=dict)
    forms: List[Dict] = field(default_factory=list)
    screenshot_path: Optional[str] = None
    raw_content: Optional[str] = None
    errors: List[str] = field(default_factory=list)
    mode: str = "mcp"


class MCPPlaywrightAnalyzer:
    """
    MCP 模式 Playwright 分析器
    
    此类设计为与 Playwright MCP Server 配合使用。
    AI Agent 通过 MCP 协议调用 Playwright 工具，此类处理返回的数据。
    
    MCP 工具调用示例:
    - playwright_navigate: 导航到页面
    - playwright_screenshot: 截取页面截图
    - playwright_click: 点击元素
    - playwright_fill: 填写表单
    - playwright_evaluate: 执行 JavaScript 获取页面信息
    
    使用方式:
    1. AI Agent 调用 MCP 工具获取页面数据
    2. 将数据传入此分析器进行结构化处理
    3. 生成测试用例和定位器
    """
    
    def __init__(self):
        self.analysis_instructions = self._get_analysis_instructions()
        self._config = get_config()

    def _get_mcp_server_config(self) -> Optional[Dict[str, Any]]:
        """Return MCP server config for Playwright, if configured."""
        mcp_config = self._config.get('analysis.mcp.playwright_mcp', {})
        if not mcp_config:
            return None

        command = mcp_config.get('command')
        if not command:
            return None

        return {
            'server_name': mcp_config.get('server_name', 'playwright'),
            'transport': mcp_config.get('transport', 'stdio'),
            'command': command,
            'args': mcp_config.get('args', []),
            'env': mcp_config.get('env', {})
        }

    async def _call_tool(self, tool: Any, params: Dict[str, Any]) -> Any:
        """Invoke a LangChain MCP tool with broad compatibility."""
        if hasattr(tool, 'ainvoke'):
            return await tool.ainvoke(params)
        if hasattr(tool, 'arun'):
            return await tool.arun(params)
        if hasattr(tool, 'invoke'):
            return tool.invoke(params)
        if hasattr(tool, 'run'):
            return tool.run(params)
        raise RuntimeError(f"Unsupported MCP tool interface: {tool}")

    def _extract_json_payload(self, raw: Any) -> Dict[str, Any]:
        """Extract JSON payload from MCP tool result."""
        if raw is None:
            return {}
        if isinstance(raw, dict):
            # Common MCP response shapes
            for key in ('content', 'result', 'data'):
                if key in raw:
                    value = raw[key]
                    if isinstance(value, str):
                        try:
                            return json.loads(value)
                        except json.JSONDecodeError:
                            return {}
                    if isinstance(value, list):
                        parts = []
                        for item in value:
                            if isinstance(item, dict):
                                if 'text' in item and isinstance(item['text'], str):
                                    parts.append(item['text'])
                                elif 'data' in item and isinstance(item['data'], str):
                                    parts.append(item['data'])
                            elif isinstance(item, str):
                                parts.append(item)
                        if parts:
                            combined = ''.join(parts)
                            try:
                                return json.loads(combined)
                            except json.JSONDecodeError:
                                return {}
            return raw
        if isinstance(raw, str):
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return {}
        return {}

    async def analyze_url(
        self,
        url: str,
        output_dir: Optional[str] = None,
        screenshot: bool = True
    ) -> MCPAnalysisResult:
        """
        Run Playwright MCP tools to analyze a URL.
        """
        server_config = self._get_mcp_server_config()
        if not server_config:
            raise RuntimeError("Playwright MCP server is not configured. Set analysis.mcp.playwright_mcp.command in config/mcp.yaml.")

        tools = await get_playwright_mcp_tools()
        tool_map = {getattr(t, 'name', ''): t for t in tools}

        navigate = tool_map.get('playwright_navigate')
        evaluate = tool_map.get('playwright_evaluate')
        screenshot_tool = tool_map.get('playwright_screenshot')

        if not navigate or not evaluate:
            raise RuntimeError("Missing MCP tools: playwright_navigate or playwright_evaluate")

        await self._call_tool(navigate, {'url': url})
        await asyncio.sleep(2)

        raw_eval = await self._call_tool(evaluate, {'script': self.generate_element_extraction_script()})
        payload = self._extract_json_payload(raw_eval)
        if not isinstance(payload, dict):
            payload = {}

        payload.setdefault('url', url)
        payload.setdefault('title', '')
        if 'raw_content' not in payload:
            payload['raw_content'] = dict(payload)

        if screenshot and screenshot_tool:
            try:
                raw_shot = await self._call_tool(screenshot_tool, {'name': 'page'})
                shot_payload = self._extract_json_payload(raw_shot)
                if isinstance(shot_payload, dict):
                    payload['screenshot_path'] = shot_payload.get('path') or shot_payload.get('screenshot_path')
            except Exception:
                payload.setdefault('screenshot_path', None)

        return self.parse_mcp_result(payload)
    
    def _get_analysis_instructions(self) -> str:
        """
        获取 MCP 分析指令
        
        返回给 AI Agent 的指令，指导如何使用 MCP 工具分析页面
        """
        return """
## Playwright MCP 分析指令

请按以下步骤使用 Playwright MCP 工具分析网页:

### 1. 导航到目标页面
```
使用 playwright_navigate 工具访问目标 URL
```

### 2. 等待页面加载
```
等待 2-3 秒确保动态内容加载完成
```

### 3. 获取页面结构
使用 playwright_evaluate 执行以下 JavaScript:

```javascript
(() => {
    const result = {
        title: document.title,
        url: window.location.href,
        elements: {
            inputs: [],
            buttons: [],
            links: [],
            selects: [],
            forms: []
        }
    };
    
    // 提取输入框
    document.querySelectorAll('input:not([type="hidden"])').forEach(el => {
        result.elements.inputs.push({
            tag: 'input',
            type: el.type || 'text',
            name: el.name,
            id: el.id,
            placeholder: el.placeholder,
            required: el.required,
            'data-testid': el.getAttribute('data-testid'),
            'aria-label': el.getAttribute('aria-label'),
            locator: getLocator(el)
        });
    });
    
    // 提取按钮
    document.querySelectorAll('button, [role="button"], input[type="submit"]').forEach(el => {
        result.elements.buttons.push({
            tag: el.tagName.toLowerCase(),
            type: el.type || 'button',
            text: el.textContent?.trim().substring(0, 50),
            name: el.name,
            id: el.id,
            'data-testid': el.getAttribute('data-testid'),
            'aria-label': el.getAttribute('aria-label'),
            disabled: el.disabled,
            locator: getLocator(el)
        });
    });
    
    // 提取链接
    document.querySelectorAll('a[href]').forEach(el => {
        result.elements.links.push({
            tag: 'a',
            text: el.textContent?.trim().substring(0, 50),
            href: el.href,
            'data-testid': el.getAttribute('data-testid'),
            locator: getLocator(el)
        });
    });
    
    // 提取下拉框
    document.querySelectorAll('select').forEach(el => {
        result.elements.selects.push({
            tag: 'select',
            name: el.name,
            id: el.id,
            options: Array.from(el.options).map(o => ({value: o.value, text: o.text})),
            locator: getLocator(el)
        });
    });
    
    // 定位器生成函数
    function getLocator(el) {
        if (el.getAttribute('data-testid')) {
            return `page.get_by_test_id('${el.getAttribute('data-testid')}')`;
        }
        if (el.getAttribute('aria-label')) {
            return `page.get_by_label('${el.getAttribute('aria-label')}')`;
        }
        if (el.placeholder) {
            return `page.get_by_placeholder('${el.placeholder}')`;
        }
        if (el.role || el.getAttribute('role')) {
            const role = el.role || el.getAttribute('role');
            const name = el.textContent?.trim() || el.getAttribute('aria-label') || '';
            return `page.get_by_role('${role}', name='${name}')`;
        }
        if (el.name) {
            return `page.locator('[name="${el.name}"]')`;
        }
        if (el.id) {
            return `page.locator('#${el.id}')`;
        }
        return `page.locator('${el.tagName.toLowerCase()}')`;
    }
    
    return JSON.stringify(result, null, 2);
})()
```

### 4. 截取页面截图
```
使用 playwright_screenshot 保存页面截图
```

### 5. 返回分析结果
将获取的数据交给分析器处理，生成测试用例
"""
    
    def parse_mcp_result(self, mcp_data: Dict[str, Any]) -> MCPAnalysisResult:
        """
        解析 MCP 工具返回的数据
        
        Args:
            mcp_data: MCP 工具返回的原始数据
        
        Returns:
            MCPAnalysisResult 结构化的分析结果
        """
        result = MCPAnalysisResult(
            url=mcp_data.get('url', ''),
            title=mcp_data.get('title', ''),
            timestamp=datetime.now().isoformat(),
            mode="mcp"
        )
        
        # 解析元素
        elements = mcp_data.get('elements', {})
        result.elements = {
            'inputs': elements.get('inputs', []),
            'buttons': elements.get('buttons', []),
            'links': elements.get('links', []),
            'selects': elements.get('selects', []),
            'forms': elements.get('forms', []),
        }
        
        # 截图路径
        result.screenshot_path = mcp_data.get('screenshot_path')
        
        # 原始内容
        result.raw_content = mcp_data.get('raw_content')
        
        return result
    
    def get_mcp_tools_required(self) -> List[Dict]:
        """
        获取需要的 MCP 工具列表
        
        Returns:
            MCP 工具描述列表
        """
        return [
            {
                'name': 'playwright_navigate',
                'description': '导航到指定 URL',
                'required_params': ['url']
            },
            {
                'name': 'playwright_screenshot',
                'description': '截取页面截图',
                'required_params': ['name']
            },
            {
                'name': 'playwright_evaluate',
                'description': '执行 JavaScript 代码',
                'required_params': ['script']
            },
            {
                'name': 'playwright_click',
                'description': '点击页面元素',
                'required_params': ['selector']
            },
            {
                'name': 'playwright_fill',
                'description': '填写表单字段',
                'required_params': ['selector', 'value']
            },
        ]
    
    def to_dict(self, result: MCPAnalysisResult) -> Dict:
        """将分析结果转换为字典"""
        return {
            'url': result.url,
            'title': result.title,
            'timestamp': result.timestamp,
            'mode': result.mode,
            'elements': result.elements,
            'forms': result.forms,
            'screenshot_path': result.screenshot_path,
            'errors': result.errors,
        }
    
    def generate_element_extraction_script(self) -> str:
        """
        生成用于 MCP playwright_evaluate 的元素提取脚本
        
        Returns:
            JavaScript 代码字符串
        """
        return '''
(() => {
    const result = {
        title: document.title,
        url: window.location.href,
        elements: {
            inputs: [],
            buttons: [],
            links: [],
            selects: [],
            textareas: [],
            checkboxes: [],
            radios: []
        }
    };
    
    function getLocator(el) {
        if (el.getAttribute('data-testid')) {
            return {type: 'testid', value: el.getAttribute('data-testid'), 
                    playwright: `page.get_by_test_id('${el.getAttribute('data-testid')}')`};
        }
        if (el.getAttribute('aria-label')) {
            return {type: 'aria-label', value: el.getAttribute('aria-label'),
                    playwright: `page.get_by_label('${el.getAttribute('aria-label')}')`};
        }
        if (el.placeholder) {
            return {type: 'placeholder', value: el.placeholder,
                    playwright: `page.get_by_placeholder('${el.placeholder}')`};
        }
        const role = el.role || el.getAttribute('role');
        if (role) {
            const name = el.textContent?.trim().substring(0, 30) || '';
            return {type: 'role', value: `${role}:${name}`,
                    playwright: `page.get_by_role('${role}', name='${name}')`};
        }
        if (el.name) {
            return {type: 'name', value: el.name,
                    playwright: `page.locator('[name="${el.name}"]')`};
        }
        if (el.id) {
            return {type: 'id', value: el.id,
                    playwright: `page.locator('#${el.id}')`};
        }
        const tag = el.tagName.toLowerCase();
        return {type: 'css', value: tag, playwright: `page.locator('${tag}')`};
    }
    
    // 提取输入框
    document.querySelectorAll('input:not([type="hidden"])').forEach(el => {
        const locator = getLocator(el);
        result.elements.inputs.push({
            tag: 'input',
            type: el.type || 'text',
            name: el.name || null,
            id: el.id || null,
            placeholder: el.placeholder || null,
            required: el.required,
            disabled: el.disabled,
            locator: locator.playwright,
            locator_type: locator.type
        });
    });
    
    // 提取按钮
    document.querySelectorAll('button, [role="button"], input[type="submit"]').forEach(el => {
        const locator = getLocator(el);
        result.elements.buttons.push({
            tag: el.tagName.toLowerCase(),
            type: el.type || 'button',
            text: el.textContent?.trim().substring(0, 50) || null,
            name: el.name || null,
            id: el.id || null,
            disabled: el.disabled,
            locator: locator.playwright,
            locator_type: locator.type
        });
    });
    
    // 提取链接
    document.querySelectorAll('a[href]').forEach(el => {
        const locator = getLocator(el);
        result.elements.links.push({
            tag: 'a',
            text: el.textContent?.trim().substring(0, 50) || null,
            href: el.href,
            locator: locator.playwright,
            locator_type: locator.type
        });
    });
    
    // 提取下拉框
    document.querySelectorAll('select').forEach(el => {
        const locator = getLocator(el);
        result.elements.selects.push({
            tag: 'select',
            name: el.name || null,
            id: el.id || null,
            required: el.required,
            options: Array.from(el.options).slice(0, 10).map(o => ({value: o.value, text: o.text})),
            locator: locator.playwright,
            locator_type: locator.type
        });
    });
    
    return JSON.stringify(result);
})()
'''
