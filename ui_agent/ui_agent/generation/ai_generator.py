"""
AI 增强模块 - 使用 OpenAI API 生成更智能的测试用例
"""

import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from ui_agent.llm import resolve_openai_config, create_openai_client


@dataclass
class AIConfig:
    """AI 配置"""
    api_key: str
    model: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000


class AITestGenerator:
    """
    AI 驱动的测试用例生成器
    
    使用 OpenAI API 分析页面结构，生成更智能的测试用例
    """
    
    def __init__(self, config: AIConfig = None):
        """
        Args:
            config: AI 配置，如果不提供则从 config/config.yaml 读取
        """
        if config:
            self.config = config
        else:
            model, api_key, base_url = resolve_openai_config()
            self.config = AIConfig(
                api_key=api_key or "",
                model=model,
                base_url=base_url,
            )
        
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required. Set it in config/config.yaml or OPENAI_API_KEY.")
        if not self.config.model:
            raise ValueError("OpenAI model is required. Set it in config/config.yaml or OPENAI_MODEL.")
        self.client = create_openai_client(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
        )
    
    def generate_test_cases(self, analysis: Dict, context: str = "") -> List[Dict]:
        """
        使用 AI 生成测试用例
        
        Args:
            analysis: 页面分析结果
            context: 额外上下文信息
        
        Returns:
            测试用例列表
        """
        # 构建提示词
        prompt = self._build_prompt(analysis, context)
        
        try:
            # 根据模型选择参数名称
            completion_params = {
                "model": self.config.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "temperature": self.config.temperature,
            }
            
            # gpt-4o/gpt-5.x 系列使用 max_completion_tokens
            if 'gpt-4o' in self.config.model or 'gpt-5' in self.config.model or 'o1' in self.config.model:
                completion_params["max_completion_tokens"] = self.config.max_tokens
            else:
                completion_params["max_tokens"] = self.config.max_tokens
            
            response = self.client.chat.completions.create(**completion_params)
            
            content = response.choices[0].message.content
            return self._parse_response(content)
            
        except Exception as e:
            print(f"AI 生成失败: {e}")
            return []
    
    def enhance_test_cases(self, test_cases: List[Dict], page_info: Dict) -> List[Dict]:
        """
        使用 AI 增强已有的测试用例
        
        Args:
            test_cases: 现有测试用例
            page_info: 页面信息
        
        Returns:
            增强后的测试用例
        """
        prompt = f"""
请分析以下测试用例，并进行增强优化：

页面信息：
{json.dumps(page_info, ensure_ascii=False, indent=2)}

现有测试用例：
{json.dumps(test_cases[:5], ensure_ascii=False, indent=2)}

请：
1. 补充缺失的边界值测试
2. 添加安全性测试用例
3. 优化测试步骤描述
4. 添加更详细的预期结果

返回增强后的测试用例，使用 JSON 格式。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.config.temperature,
            )
            
            content = response.choices[0].message.content
            enhanced = self._parse_response(content)
            
            # 合并原有和增强的用例
            return test_cases + enhanced
            
        except Exception as e:
            print(f"AI 增强失败: {e}")
            return test_cases
    
    def analyze_figma_design(self, figma_data: Dict) -> Dict:
        """
        使用 AI 分析 Figma 设计稿
        
        Args:
            figma_data: Figma API 返回的数据
        
        Returns:
            分析结果
        """
        # 提取关键信息
        components = self._extract_figma_components(figma_data)
        
        prompt = f"""
分析以下 Figma 设计稿的组件信息，识别：
1. 页面类型（登录、列表、详情、表单等）
2. 主要交互元素
3. 可能的用户操作流程
4. 需要测试的功能点

组件信息：
{json.dumps(components, ensure_ascii=False, indent=2)}

请返回 JSON 格式的分析结果。
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的 UI/UX 分析师，擅长从设计稿中识别功能和测试点。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
            )
            
            content = response.choices[0].message.content
            return self._parse_json_response(content)
            
        except Exception as e:
            print(f"AI 分析 Figma 失败: {e}")
            return {}
    
    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的软件测试专家，擅长编写高质量的测试用例。

你的输出应该：
1. 使用 JSON 格式
2. 包含完整的测试用例结构（id, title, priority, preconditions, steps, expected_result）
3. 覆盖正向、负向、边界值测试
4. 考虑安全性和性能测试
5. 步骤描述清晰、可执行

优先级说明：
- P0: 核心功能，阻塞级别
- P1: 重要功能，必须测试
- P2: 一般功能，建议测试
- P3: 边缘场景，可选测试
"""
    
    def _build_prompt(self, analysis: Dict, context: str) -> str:
        """构建提示词"""
        # 提取关键信息
        title = analysis.get('title', '')
        url = analysis.get('url', '')
        elements = analysis.get('elements', {})
        forms = analysis.get('forms', [])
        api_requests = analysis.get('api_requests', [])
        
        # 提取有意义的按钮（有文本的）
        buttons = [b for b in elements.get('buttons', []) if b.get('text')]
        
        # 提取链接（去重）
        links = elements.get('links', [])
        unique_links = []
        seen_texts = set()
        for link in links:
            text = link.get('text', '').strip()
            if text and text not in seen_texts:
                seen_texts.add(text)
                unique_links.append({'text': text, 'href': link.get('href', '')})
        
        # 提取表格信息
        tables = elements.get('tables', [])
        table_info = []
        for t in tables:
            table_info.append({
                'headers': t.get('headers', []),
                'row_count': t.get('row_count', 0),
                'has_checkbox': t.get('has_checkbox', False),
                'has_actions': t.get('has_actions', False),
                'sample_data': t.get('sample_data', [])[:2]  # 只取2行示例
            })
        
        # 提取 API 端点
        api_endpoints = []
        for api in api_requests[:10]:
            api_endpoints.append({
                'url': api.get('url', ''),
                'method': api.get('method', '')
            })
        
        # 分析页面类型
        page_type = self._detect_page_type(title, url, elements, forms)
        
        page_info = {
            'title': title,
            'url': url,
            'page_type': page_type,
            'elements': {
                'input_count': len(elements.get('inputs', [])),
                'button_count': len(buttons),
                'link_count': len(unique_links),
                'table_count': len(tables),
                'form_count': len(forms)
            },
            'buttons': [{'text': b.get('text'), 'disabled': b.get('disabled')} for b in buttons[:15]],
            'navigation_links': unique_links[:10],
            'tables': table_info,
            'forms': [{'fields': f.get('fields', [])} for f in forms[:3]],
            'api_endpoints': api_endpoints
        }
        
        prompt = f"""
请为以下页面生成功能测试用例：

## 页面信息
{json.dumps(page_info, ensure_ascii=False, indent=2)}

{f"额外上下文：{context}" if context else ""}

## 要求
1. 根据页面类型（{page_type}）生成 **针对性** 的测试用例
2. 测试用例标题必须包含 **具体的功能名称**，如"验证 ZD620 打印机详情页面跳转"，不要用"验证按钮点击"这种泛化描述
3. 测试步骤要具体，包含实际的元素名称和操作
4. 生成 8-15 个测试用例，覆盖：
   - 页面主要功能的正向测试
   - 数据展示验证（表格数据、列表项）
   - 导航功能测试
   - 筛选/搜索功能（如果有）
   - 操作按钮功能
   - 边界情况和异常处理

5. 每个用例格式：
   {{
     "id": "TC_XXX",
     "title": "具体的测试标题 - 包含功能名称",
     "priority": "P0/P1/P2/P3",
     "preconditions": ["已登录系统", "进入XXX页面"],
     "steps": ["点击XXX按钮", "输入XXX数据", "验证XXX"],
     "expected_result": "具体的预期结果"
   }}

返回 JSON 数组格式。
"""
        return prompt
    
    def _detect_page_type(self, title: str, url: str, elements: Dict, forms: List) -> str:
        """检测页面类型"""
        url_lower = url.lower()
        title_lower = title.lower()
        
        # 根据 URL 和标题推断页面类型
        if 'login' in url_lower or 'signin' in url_lower:
            return "登录页面"
        if 'device' in url_lower or 'printer' in url_lower:
            if elements.get('tables'):
                return "设备列表页面"
            return "设备管理页面"
        if 'setting' in url_lower or 'config' in url_lower:
            return "设置页面"
        if 'dashboard' in url_lower or 'home' in url_lower:
            return "仪表盘/首页"
        if 'detail' in url_lower or any(char.isdigit() for char in url.split('/')[-1]):
            return "详情页面"
        if forms:
            return "表单页面"
        if elements.get('tables'):
            return "数据列表页面"
        
        return "通用页面"
    
    def _parse_response(self, content: str) -> List[Dict]:
        """解析 AI 响应"""
        return self._parse_json_response(content) or []
    
    def _parse_json_response(self, content: str) -> Any:
        """解析 JSON 响应"""
        try:
            # 尝试直接解析
            return json.loads(content)
        except json.JSONDecodeError:
            # 尝试提取 JSON 块
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)```', content)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 尝试找到 [ 或 { 开头的部分
            for start_char, end_char in [('[', ']'), ('{', '}')]:
                start = content.find(start_char)
                if start != -1:
                    # 找到匹配的结束符
                    depth = 0
                    for i, c in enumerate(content[start:]):
                        if c == start_char:
                            depth += 1
                        elif c == end_char:
                            depth -= 1
                            if depth == 0:
                                try:
                                    return json.loads(content[start:start+i+1])
                                except:
                                    break
        return None
    
    def _extract_figma_components(self, figma_data: Dict) -> List[Dict]:
        """从 Figma 数据中提取组件信息"""
        components = []
        
        def extract_node(node, depth=0):
            if depth > 5:  # 限制深度
                return
            
            node_type = node.get('type', '')
            name = node.get('name', '')
            
            # 识别可能的 UI 元素
            if node_type in ['COMPONENT', 'INSTANCE', 'FRAME', 'GROUP']:
                comp_info = {
                    'name': name,
                    'type': node_type,
                }
                
                # 猜测元素类型
                name_lower = name.lower()
                if any(kw in name_lower for kw in ['button', 'btn', '按钮']):
                    comp_info['ui_type'] = 'button'
                elif any(kw in name_lower for kw in ['input', 'field', 'text', '输入']):
                    comp_info['ui_type'] = 'input'
                elif any(kw in name_lower for kw in ['modal', 'dialog', 'popup', '弹窗']):
                    comp_info['ui_type'] = 'modal'
                elif any(kw in name_lower for kw in ['table', '表格', 'list', '列表']):
                    comp_info['ui_type'] = 'table'
                elif any(kw in name_lower for kw in ['nav', 'menu', '导航', '菜单']):
                    comp_info['ui_type'] = 'navigation'
                elif any(kw in name_lower for kw in ['form', '表单']):
                    comp_info['ui_type'] = 'form'
                
                if 'ui_type' in comp_info:
                    components.append(comp_info)
            
            # 递归处理子节点
            for child in node.get('children', []):
                extract_node(child, depth + 1)
        
        # 从根节点开始
        document = figma_data.get('document', figma_data)
        extract_node(document)
        
        return components[:50]  # 限制数量


def generate_with_ai(analysis: Dict, context: str = "") -> List[Dict]:
    """
    便捷函数：使用 AI 生成测试用例
    
    Args:
        analysis: 页面分析结果
        context: 额外上下文
    
    Returns:
        测试用例列表
    """
    try:
        generator = AITestGenerator()
        return generator.generate_test_cases(analysis, context)
    except Exception as e:
        print(f"AI 生成不可用: {e}")
        return []
