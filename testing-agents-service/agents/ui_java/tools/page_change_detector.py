"""
页面变更检测器

使用 Playwright MCP 获取页面元素，与现有 PageObject 对比，
检测定位器变化，生成变更报告和全新的 PageObject 类。

匹配策略（分层）：
1. 高置信度匹配（纯代码）：data-testid 完全匹配、ID 完全匹配
2. 中置信度匹配（代码+规则）：文本相似、属性部分匹配
3. 低置信度匹配（需 AI 辅助）：语义理解、跨语言匹配
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Callable
import json


class ChangeType(Enum):
    """变更类型"""
    UNCHANGED = "unchanged"      # 未变更
    MODIFIED = "modified"        # 已修改
    ADDED = "added"              # 新增
    DELETED = "deleted"          # 已删除


@dataclass
class PageElement:
    """页面元素（来自 Playwright MCP browser_snapshot）"""
    tag: str                     # 元素标签 (button, input, a, etc.)
    text: Optional[str] = None   # 元素文本
    role: Optional[str] = None   # ARIA 角色
    aria_label: Optional[str] = None
    placeholder: Optional[str] = None
    data_testid: Optional[str] = None
    type: Optional[str] = None   # input type
    href: Optional[str] = None   # 链接地址
    name: Optional[str] = None   # name 属性
    id: Optional[str] = None     # id 属性
    class_name: Optional[str] = None  # class 属性
    selector: Optional[str] = None    # 推荐的选择器
    ref: Optional[str] = None    # Playwright MCP 返回的 ref
    
    def get_best_locator(self) -> str:
        """获取最佳定位器（按优先级）"""
        if self.data_testid:
            return f'page.locator("[data-testid=\'{self.data_testid}\']")'
        
        if self.aria_label:
            return f'page.getByLabel("{self.aria_label}")'
        
        if self.role:
            role_upper = self.role.upper()
            if self.text:
                return f'page.getByRole(AriaRole.{role_upper}, new Options().setName("{self.text}"))'
            return f'page.getByRole(AriaRole.{role_upper})'
        
        if self.placeholder:
            return f'page.getByPlaceholder("{self.placeholder}")'
        
        if self.text and len(self.text) < 30:
            return f'page.getByText("{self.text}")'
        
        if self.id:
            return f'page.locator("#{self.id}")'
        
        if self.selector:
            return f'page.locator("{self.selector}")'
        
        return f'page.locator("{self.tag}")'
    
    def to_method_name(self) -> str:
        """生成方法名"""
        # 优先使用有意义的属性
        name_source = (
            self.data_testid or 
            self.aria_label or 
            self.placeholder or 
            self.text or 
            self.name or 
            self.id or 
            self.tag
        )
        
        # 清理并转换为驼峰命名
        clean_name = re.sub(r'[^\w\s]', '', name_source or 'element')
        words = clean_name.split()[:4]  # 最多取 4 个词
        
        if not words:
            return f"{self.tag}Element"
        
        # 首字母小写的驼峰命名
        result = words[0].lower()
        for word in words[1:]:
            result += word.capitalize()
        
        # 根据元素类型添加后缀
        type_suffixes = {
            'button': 'Button',
            'input': 'Input',
            'a': 'Link',
            'select': 'Select',
            'textarea': 'TextArea',
            'checkbox': 'Checkbox',
            'radio': 'Radio',
        }
        
        tag_lower = self.tag.lower()
        if tag_lower in type_suffixes and not result.endswith(type_suffixes[tag_lower]):
            if self.type == 'checkbox':
                result += 'Checkbox'
            elif self.type == 'radio':
                result += 'Radio'
            else:
                result += type_suffixes[tag_lower]
        
        return result


@dataclass
class LocatorMethod:
    """PageObject 中的定位器方法"""
    name: str                    # 方法名
    locator: str                 # 定位器表达式
    return_type: str = "Locator"
    comment: Optional[str] = None
    line_number: int = 0


class ConfidenceLevel(Enum):
    """置信度级别"""
    HIGH = "high"          # 0.9-1.0 纯代码可靠
    MEDIUM = "medium"      # 0.6-0.89 代码较可靠
    LOW = "low"            # 0.3-0.59 需要确认
    NONE = "none"          # < 0.3 未匹配


@dataclass
class LocatorChange:
    """定位器变更记录"""
    method_name: str
    change_type: ChangeType
    old_locator: Optional[str] = None
    new_locator: Optional[str] = None
    old_element: Optional[PageElement] = None
    new_element: Optional[PageElement] = None
    reason: str = ""
    confidence: float = 1.0      # 匹配置信度 (0-1)
    needs_review: bool = False   # 是否需要人工/AI 确认
    
    @property
    def confidence_level(self) -> ConfidenceLevel:
        """获取置信度级别"""
        if self.confidence >= 0.9:
            return ConfidenceLevel.HIGH
        elif self.confidence >= 0.6:
            return ConfidenceLevel.MEDIUM
        elif self.confidence >= 0.3:
            return ConfidenceLevel.LOW
        return ConfidenceLevel.NONE
    
    @property
    def is_reliable(self) -> bool:
        """匹配是否可靠（纯代码判断）"""
        return self.confidence >= 0.6


class PageObjectParser:
    """解析 Java PageObject 文件"""
    
    @staticmethod
    def parse(java_code: str) -> Tuple[str, List[LocatorMethod]]:
        """
        解析 Java PageObject 代码
        
        Args:
            java_code: Java 源代码
        
        Returns:
            (类名, 定位器方法列表)
        """
        # 提取类名
        class_match = re.search(r'class\s+(\w+)', java_code)
        class_name = class_match.group(1) if class_match else "UnknownPage"
        
        methods = []
        
        # 匹配方法定义
        # public Locator methodName() { return page.locator("..."); }
        method_pattern = re.compile(
            r'(?:/\*\*?\s*(.*?)\s*\*/\s*)?'  # 可选的注释
            r'public\s+(\w+)\s+(\w+)\s*\(\s*\)\s*\{'  # 方法签名
            r'\s*return\s+(.*?);'  # return 语句
            r'\s*\}',
            re.DOTALL
        )
        
        for match in method_pattern.finditer(java_code):
            comment = match.group(1)
            return_type = match.group(2)
            method_name = match.group(3)
            locator_expr = match.group(4).strip()
            
            if return_type in ('Locator', 'Page'):
                methods.append(LocatorMethod(
                    name=method_name,
                    locator=locator_expr,
                    return_type=return_type,
                    comment=comment.strip() if comment else None,
                    line_number=java_code[:match.start()].count('\n') + 1
                ))
        
        return class_name, methods


class PlaywrightMCPElementParser:
    """解析 Playwright MCP browser_snapshot 返回的元素"""
    
    @staticmethod
    def parse_snapshot(snapshot_data: str) -> List[PageElement]:
        """
        解析 browser_snapshot 返回的数据
        
        Args:
            snapshot_data: browser_snapshot 返回的 JSON 或文本
        
        Returns:
            PageElement 列表
        """
        elements = []
        
        # 尝试 JSON 解析
        try:
            data = json.loads(snapshot_data) if isinstance(snapshot_data, str) else snapshot_data
            if isinstance(data, list):
                for item in data:
                    element = PlaywrightMCPElementParser._parse_element_dict(item)
                    if element:
                        elements.append(element)
            elif isinstance(data, dict) and 'elements' in data:
                for item in data['elements']:
                    element = PlaywrightMCPElementParser._parse_element_dict(item)
                    if element:
                        elements.append(element)
        except (json.JSONDecodeError, TypeError):
            # 解析文本格式
            elements = PlaywrightMCPElementParser._parse_text_snapshot(snapshot_data)
        
        return elements
    
    @staticmethod
    def _parse_element_dict(item: dict) -> Optional[PageElement]:
        """从字典解析元素"""
        if not item:
            return None
        
        return PageElement(
            tag=item.get('tag', item.get('tagName', 'element')),
            text=item.get('text', item.get('innerText', '')),
            role=item.get('role'),
            aria_label=item.get('aria-label', item.get('ariaLabel')),
            placeholder=item.get('placeholder'),
            data_testid=item.get('data-testid', item.get('dataTestid')),
            type=item.get('type'),
            href=item.get('href'),
            name=item.get('name'),
            id=item.get('id'),
            class_name=item.get('class', item.get('className')),
            selector=item.get('selector'),
            ref=item.get('ref')
        )
    
    @staticmethod
    def _parse_text_snapshot(text: str) -> List[PageElement]:
        """解析文本格式的快照（Playwright MCP 默认格式）"""
        elements = []
        
        # Playwright MCP 常见格式：
        # - [ref=e1] button "Login"
        # - [ref=e2] input [placeholder="Username"]
        # - [ref=e3] link "About Us" [href="/about"]
        
        lines = text.strip().split('\n')
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            element = PlaywrightMCPElementParser._parse_element_line(line)
            if element:
                elements.append(element)
        
        return elements
    
    @staticmethod
    def _parse_element_line(line: str) -> Optional[PageElement]:
        """解析单行元素描述"""
        # 示例: - [ref=e1] button "Login" [data-testid="login-btn"]
        
        element = PageElement(tag='element')
        
        # 提取 ref
        ref_match = re.search(r'\[ref=(\w+)\]', line)
        if ref_match:
            element.ref = ref_match.group(1)
        
        # 提取标签类型
        tag_match = re.search(r'\]\s*(\w+)\s', line)
        if tag_match:
            element.tag = tag_match.group(1)
        
        # 提取引号内的文本
        text_match = re.search(r'"([^"]+)"', line)
        if text_match:
            element.text = text_match.group(1)
        
        # 提取属性
        attrs = re.findall(r'\[(\w+(?:-\w+)*)=["\']?([^"\'\]]+)["\']?\]', line)
        for attr_name, attr_value in attrs:
            if attr_name == 'placeholder':
                element.placeholder = attr_value
            elif attr_name == 'data-testid':
                element.data_testid = attr_value
            elif attr_name == 'aria-label':
                element.aria_label = attr_value
            elif attr_name == 'href':
                element.href = attr_value
            elif attr_name == 'type':
                element.type = attr_value
            elif attr_name == 'id':
                element.id = attr_value
        
        return element


class PageChangeDetector:
    """
    页面变更检测器
    
    对比 Playwright MCP 获取的当前页面元素与旧 PageObject 类，
    检测定位器变化并生成更新后的 PageObject。
    """
    
    def __init__(self, workspace_path: Path = None):
        """
        初始化检测器
        
        Args:
            workspace_path: 工作区路径（用于保存报告和新 Page 类）
        """
        self.workspace_path = workspace_path
    
    def detect_changes(
        self,
        old_page_code: str,
        current_elements: List[PageElement]
    ) -> List[LocatorChange]:
        """
        检测变更
        
        Args:
            old_page_code: 旧的 PageObject Java 代码
            current_elements: 当前页面元素（来自 Playwright MCP）
        
        Returns:
            变更列表
        """
        # 解析旧 PageObject
        class_name, old_methods = PageObjectParser.parse(old_page_code)
        
        changes = []
        matched_elements = set()
        
        # 对比每个旧方法
        for method in old_methods:
            best_match = self._find_best_match(method, current_elements)
            
            if best_match:
                element, confidence = best_match
                matched_elements.add(id(element))
                
                new_locator = element.get_best_locator()
                # 低置信度匹配需要人工确认
                needs_review = confidence < 0.6
                
                # 判断是否有变化
                if self._locators_equivalent(method.locator, new_locator):
                    changes.append(LocatorChange(
                        method_name=method.name,
                        change_type=ChangeType.UNCHANGED,
                        old_locator=method.locator,
                        new_locator=new_locator,
                        confidence=confidence,
                        needs_review=needs_review
                    ))
                else:
                    reason = self._get_change_reason(method.locator, new_locator)
                    if needs_review:
                        reason = f"⚠️ 需确认: {reason}"
                    changes.append(LocatorChange(
                        method_name=method.name,
                        change_type=ChangeType.MODIFIED,
                        old_locator=method.locator,
                        new_locator=new_locator,
                        new_element=element,
                        reason=reason,
                        confidence=confidence,
                        needs_review=needs_review
                    ))
            else:
                # 未找到匹配 - 可能已删除，需要确认
                changes.append(LocatorChange(
                    method_name=method.name,
                    change_type=ChangeType.DELETED,
                    old_locator=method.locator,
                    reason="⚠️ 需确认: 元素在当前页面中未找到",
                    needs_review=True  # 删除操作总是需要确认
                ))
        
        # 检测新增元素
        for element in current_elements:
            if id(element) not in matched_elements:
                # 只记录可交互的重要元素
                if element.tag in ('button', 'a', 'input', 'select', 'textarea'):
                    changes.append(LocatorChange(
                        method_name=element.to_method_name(),
                        change_type=ChangeType.ADDED,
                        new_locator=element.get_best_locator(),
                        new_element=element,
                        reason="新增元素"
                    ))
        
        return changes
    
    def _find_best_match(
        self,
        method: LocatorMethod,
        elements: List[PageElement]
    ) -> Optional[Tuple[PageElement, float]]:
        """
        为旧方法找到最匹配的当前元素（分层匹配策略）
        
        匹配层级：
        1. 高置信度（0.9-1.0）：唯一标识符完全匹配，纯代码可靠
        2. 中置信度（0.6-0.89）：多属性组合匹配，代码较可靠
        3. 低置信度（0.3-0.59）：模糊匹配，需 AI 辅助确认
        
        Returns:
            (匹配的元素, 置信度) 或 None
        """
        # 第一轮：高置信度匹配（纯代码100%可靠）
        for element in elements:
            score = self._high_confidence_match(method, element)
            if score >= 0.9:
                return (element, score)
        
        # 第二轮：中置信度匹配（代码较可靠）
        best_match = None
        best_score = 0.0
        for element in elements:
            score = self._medium_confidence_match(method, element)
            if score > best_score:
                best_score = score
                best_match = element
        
        if best_score >= 0.6:
            return (best_match, best_score)
        
        # 第三轮：低置信度匹配（需要 AI 辅助或人工确认）
        for element in elements:
            score = self._low_confidence_match(method, element)
            if score > best_score:
                best_score = score
                best_match = element
        
        if best_score >= 0.3:
            return (best_match, best_score)
        
        return None
    
    def _high_confidence_match(self, method: LocatorMethod, element: PageElement) -> float:
        """
        高置信度匹配（0.9-1.0）- 纯代码100%可靠
        
        基于唯一标识符的精确匹配：
        - data-testid 完全匹配
        - ID 完全匹配
        - 定位器字符串完全匹配
        """
        locator = method.locator.lower()
        
        # 1. data-testid 完全匹配（最可靠）
        if element.data_testid:
            testid_lower = element.data_testid.lower()
            # 检查定位器中是否包含完整的 testid
            if f"data-testid='{testid_lower}'" in locator or \
               f'data-testid="{testid_lower}"' in locator or \
               f"data-testid={testid_lower}" in locator:
                return 1.0
            # 检查 getByTestId
            if f"getbytestid(\"{testid_lower}\")" in locator or \
               f"getbytestid('{testid_lower}')" in locator:
                return 1.0
        
        # 2. ID 完全匹配
        if element.id:
            id_lower = element.id.lower()
            # 检查 #id 选择器
            if f"#{id_lower}" in locator or f"#{id_lower}\"" in locator or f"#{id_lower}'" in locator:
                return 0.95
            # 检查 [id='xxx']
            if f"id='{id_lower}'" in locator or f'id="{id_lower}"' in locator:
                return 0.95
        
        # 3. 精确的 placeholder 匹配
        if element.placeholder:
            placeholder_lower = element.placeholder.lower()
            if f"getbyplaceholder(\"{placeholder_lower}\")" in locator or \
               f"getbyplaceholder('{placeholder_lower}')" in locator or \
               f"placeholder='{placeholder_lower}'" in locator or \
               f'placeholder="{placeholder_lower}"' in locator:
                return 0.92
        
        # 4. 精确的 aria-label 匹配
        if element.aria_label:
            label_lower = element.aria_label.lower()
            if f"getbylabel(\"{label_lower}\")" in locator or \
               f"getbylabel('{label_lower}')" in locator or \
               f"aria-label='{label_lower}'" in locator or \
               f'aria-label="{label_lower}"' in locator:
                return 0.92
        
        return 0.0
    
    def _medium_confidence_match(self, method: LocatorMethod, element: PageElement) -> float:
        """
        中置信度匹配（0.6-0.89）- 代码较可靠
        
        基于多属性组合的匹配：
        - 文本 + 元素类型
        - 部分属性匹配
        - 方法名语义推断
        """
        score = 0.0
        locator = method.locator.lower()
        method_name = method.name.lower()
        
        # 1. 文本精确匹配 + 元素类型匹配
        if element.text:
            text_lower = element.text.lower()
            # 定位器中包含完整文本
            if f'"{element.text}"' in method.locator or f"'{element.text}'" in method.locator:
                score += 0.5
                # 如果元素类型也匹配，更可靠
                if element.tag.lower() in locator:
                    score += 0.2
            # getByText 匹配
            elif f"getbytext(\"{text_lower}\")" in locator or f"getbytext('{text_lower}')" in locator:
                score += 0.6
        
        # 2. Role + Name 组合匹配
        if element.role and element.text:
            role_lower = element.role.lower()
            if f"getbyrole(ariarole.{role_lower}" in locator:
                score += 0.3
                if element.text.lower() in locator:
                    score += 0.3
        
        # 3. 部分 ID/testid 匹配（处理 ID 变化但核心不变的情况）
        if element.data_testid:
            testid_parts = re.split(r'[-_]', element.data_testid.lower())
            for part in testid_parts:
                if len(part) > 2 and part in locator:
                    score += 0.15
        
        if element.id:
            id_parts = re.split(r'[-_]', element.id.lower())
            for part in id_parts:
                if len(part) > 2 and part in locator:
                    score += 0.1
        
        # 4. 方法名与元素属性的直接匹配
        if element.data_testid and element.data_testid.lower() == method_name:
            score += 0.4
        
        if element.text:
            # 方法名包含元素文本（同语言）
            text_normalized = re.sub(r'[^\w]', '', element.text.lower())
            method_normalized = re.sub(r'[^\w]', '', method_name)
            if text_normalized and text_normalized in method_normalized:
                score += 0.25
        
        return min(score, 0.89)
    
    def _low_confidence_match(self, method: LocatorMethod, element: PageElement) -> float:
        """
        低置信度匹配（0.3-0.59）- 需要 AI 辅助或人工确认
        
        基于模糊匹配：
        - 部分文本相似
        - 元素类型相似
        - 位置推断
        
        注意：这些匹配应该标记为"需要确认"
        """
        score = 0.0
        method_name = method.name.lower()
        locator = method.locator.lower()
        
        # 1. 元素类型匹配
        tag_to_suffix = {
            'button': ['button', 'btn'],
            'input': ['input', 'field', 'textbox'],
            'a': ['link', 'anchor'],
            'select': ['select', 'dropdown', 'combo'],
            'textarea': ['textarea', 'text'],
        }
        
        for tag, suffixes in tag_to_suffix.items():
            if element.tag.lower() == tag:
                for suffix in suffixes:
                    if suffix in method_name:
                        score += 0.15
                        break
        
        # 2. 部分文本模糊匹配
        if element.text:
            # 取文本中的关键词
            text_words = set(re.findall(r'\w+', element.text.lower()))
            method_words = set(re.findall(r'[a-z]+', method_name))
            
            common_words = text_words & method_words
            if common_words:
                score += 0.1 * len(common_words)
        
        # 3. 属性存在性匹配（弱匹配）
        if element.placeholder and 'placeholder' in locator:
            score += 0.1
        
        if element.href and ('link' in method_name or 'href' in locator):
            score += 0.1
        
        return min(score, 0.59)
    
    def _calculate_match_score(self, method: LocatorMethod, element: PageElement) -> float:
        """
        计算方法与元素的匹配分数 (0-1)
        
        综合三层匹配策略的结果
        """
        # 优先尝试高置信度匹配
        high_score = self._high_confidence_match(method, element)
        if high_score >= 0.9:
            return high_score
        
        # 尝试中置信度匹配
        medium_score = self._medium_confidence_match(method, element)
        if medium_score >= 0.6:
            return medium_score
        
        # 低置信度匹配
        low_score = self._low_confidence_match(method, element)
        return max(high_score, medium_score, low_score)
    
    def _locators_equivalent(self, old_locator: str, new_locator: str) -> bool:
        """判断两个定位器是否等效"""
        # 简单比较（忽略空白和引号差异）
        old_clean = re.sub(r'[\s\'"]', '', old_locator.lower())
        new_clean = re.sub(r'[\s\'"]', '', new_locator.lower())
        return old_clean == new_clean
    
    def _get_change_reason(self, old_locator: str, new_locator: str) -> str:
        """分析变更原因"""
        if 'data-testid' in new_locator and 'data-testid' not in old_locator:
            return "升级为更稳定的 data-testid 定位器"
        
        if 'getByRole' in new_locator and 'getByRole' not in old_locator:
            return "升级为语义化的 Role 定位器"
        
        if 'getByLabel' in new_locator or 'getByPlaceholder' in new_locator:
            return "定位器文本内容已更新"
        
        return "选择器已更新"
    
    def generate_new_page_object(
        self,
        class_name: str,
        changes: List[LocatorChange],
        url: str = ""
    ) -> str:
        """
        生成全新的 PageObject 类
        
        Args:
            class_name: 类名
            changes: 变更列表
            url: 页面 URL
        
        Returns:
            Java 代码
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 统计
        modified_count = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)
        added_count = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
        deleted_count = sum(1 for c in changes if c.change_type == ChangeType.DELETED)
        
        # 统计需要确认的数量
        needs_review_count = sum(1 for c in changes if c.needs_review)
        
        # 生成变更记录注释
        change_notes = []
        for c in changes:
            review_mark = "[需确认] " if c.needs_review else ""
            confidence_mark = f"({c.confidence:.0%})" if c.change_type != ChangeType.UNCHANGED else ""
            if c.change_type == ChangeType.MODIFIED:
                change_notes.append(f" * - {review_mark}{c.method_name}{confidence_mark}: {c.old_locator} → {c.new_locator}")
            elif c.change_type == ChangeType.ADDED:
                change_notes.append(f" * - 新增: {c.method_name}")
            elif c.change_type == ChangeType.DELETED:
                change_notes.append(f" * - {review_mark}已删除: {c.method_name}")
        
        change_notes_str = '\n'.join(change_notes) if change_notes else " * 无变更"
        
        review_warning = ""
        if needs_review_count > 0:
            review_warning = f""" *
 * ⚠️ 警告: {needs_review_count} 项变更需要人工确认（置信度 < 60%）
 * 标记为 [需确认] 的项目基于模糊匹配，建议人工核实后再使用
 *"""
        
        code_lines = [
            f'/**',
            f' * {class_name} - 自动生成于 {timestamp}',
            f' * URL: {url}',
            f' *',
            f' * 变更统计: 修改 {modified_count}, 新增 {added_count}, 删除 {deleted_count}',
            review_warning,
            f' * 变更记录:',
            change_notes_str,
            f' */',
            f'public class {class_name} {{',
            f'    private final Page page;',
            f'',
            f'    public {class_name}(Page page) {{',
            f'        this.page = page;',
            f'    }}',
            f''
        ]
        
        # 生成方法
        for change in changes:
            review_tag = "// TODO: 需人工确认此匹配\n    " if change.needs_review else ""
            confidence_info = f"@置信度 {change.confidence:.0%}" if change.change_type == ChangeType.MODIFIED else ""
            
            if change.change_type == ChangeType.DELETED:
                # 已删除的方法标记为 @Deprecated
                code_lines.extend([
                    f'    /**',
                    f'     * @deprecated 元素已从页面移除 (需人工确认)',
                    f'     */',
                    f'    @Deprecated',
                    f'    {review_tag}public Locator {change.method_name}() {{',
                    f'        // 原定位器: {change.old_locator}',
                    f'        throw new RuntimeException("元素已移除: {change.method_name}");',
                    f'    }}',
                    f''
                ])
            elif change.change_type == ChangeType.MODIFIED:
                # 已修改的方法
                review_line = f'     * ⚠️ 低置信度匹配，请人工确认\n' if change.needs_review else ''
                code_lines.extend([
                    f'    /**',
                    f'     * {change.method_name}',
                    f'{review_line}     * @变更 {change.reason}',
                    f'     * {confidence_info}',
                    f'     * @旧定位器 {change.old_locator}',
                    f'     */',
                    f'    {review_tag}public Locator {change.method_name}() {{',
                    f'        return {change.new_locator};',
                    f'    }}',
                    f''
                ])
            elif change.change_type == ChangeType.ADDED:
                # 新增的方法
                code_lines.extend([
                    f'    /**',
                    f'     * {change.method_name}',
                    f'     * @新增 {timestamp[:10]}',
                    f'     */',
                    f'    public Locator {change.method_name}() {{',
                    f'        return {change.new_locator};',
                    f'    }}',
                    f''
                ])
            else:
                # 未变更的方法
                code_lines.extend([
                    f'    /**',
                    f'     * {change.method_name}',
                    f'     */',
                    f'    public Locator {change.method_name}() {{',
                    f'        return {change.new_locator or change.old_locator};',
                    f'    }}',
                    f''
                ])
        
        code_lines.append('}')
        
        return '\n'.join(code_lines)
    
    def generate_html_report(
        self,
        class_name: str,
        changes: List[LocatorChange],
        url: str = ""
    ) -> str:
        """
        生成 HTML 格式的变更报告（突出显示置信度级别）
        
        Args:
            class_name: 类名
            changes: 变更列表
            url: 页面 URL
        
        Returns:
            HTML 代码
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 变更类型统计
        total = len(changes)
        unchanged = sum(1 for c in changes if c.change_type == ChangeType.UNCHANGED)
        modified = sum(1 for c in changes if c.change_type == ChangeType.MODIFIED)
        added = sum(1 for c in changes if c.change_type == ChangeType.ADDED)
        deleted = sum(1 for c in changes if c.change_type == ChangeType.DELETED)
        
        # 置信度级别统计
        high_conf = sum(1 for c in changes if c.confidence >= 0.9)
        medium_conf = sum(1 for c in changes if 0.6 <= c.confidence < 0.9)
        low_conf = sum(1 for c in changes if 0.3 <= c.confidence < 0.6)
        needs_review = sum(1 for c in changes if c.needs_review)
        
        # 可靠性评估
        reliability_score = (high_conf * 100 + medium_conf * 70 + low_conf * 40) / max(total, 1)
        reliability_label = "优秀" if reliability_score >= 80 else "良好" if reliability_score >= 60 else "需审核"
        reliability_color = "#4caf50" if reliability_score >= 80 else "#ffc107" if reliability_score >= 60 else "#f44336"
        
        # 生成变更行
        change_rows = []
        for change in changes:
            # 状态图标
            icon = {
                ChangeType.UNCHANGED: '✅',
                ChangeType.MODIFIED: '🔄',
                ChangeType.ADDED: '➕',
                ChangeType.DELETED: '❌'
            }.get(change.change_type, '•')
            
            # 行样式类
            status_class = {
                ChangeType.UNCHANGED: 'unchanged',
                ChangeType.MODIFIED: 'modified',
                ChangeType.ADDED: 'added',
                ChangeType.DELETED: 'deleted'
            }.get(change.change_type, '')
            
            # 置信度样式
            if change.confidence >= 0.9:
                conf_class = "conf-high"
                conf_icon = "🟢"
                conf_label = "高"
            elif change.confidence >= 0.6:
                conf_class = "conf-medium"
                conf_icon = "🟡"
                conf_label = "中"
            else:
                conf_class = "conf-low"
                conf_icon = "🔴"
                conf_label = "低"
            
            # 需要确认的标记
            review_badge = '<span class="review-badge">⚠️ 需确认</span>' if change.needs_review else ''
            
            old_loc = self._escape_html(change.old_locator or '-')
            new_loc = self._escape_html(change.new_locator or '-')
            reason = self._escape_html(change.reason or '')
            
            # 添加需要确认的行样式
            row_class = f"{status_class} {'needs-review' if change.needs_review else ''}"
            
            change_rows.append(f'''
            <tr class="{row_class}">
                <td class="status-cell">{icon}</td>
                <td class="method-cell">
                    <code>{change.method_name}</code>
                    {review_badge}
                </td>
                <td class="locator-cell"><code class="old">{old_loc}</code></td>
                <td class="locator-cell"><code class="new">{new_loc}</code></td>
                <td class="reason-cell">{reason}</td>
                <td class="conf-cell {conf_class}">
                    <span class="conf-badge">{conf_icon} {change.confidence:.0%}</span>
                    <span class="conf-label">{conf_label}</span>
                </td>
            </tr>
            ''')
        
        # 需要确认的警告区块
        warning_section = ""
        if needs_review > 0:
            warning_section = f'''
        <div class="warning-banner">
            <div class="warning-icon">⚠️</div>
            <div class="warning-content">
                <h3>{needs_review} 项变更需要人工确认</h3>
                <p>这些匹配基于模糊算法，置信度低于 60%，建议人工核实后再应用。</p>
                <ul>
                    <li><strong>低置信度匹配</strong>: 可能存在误匹配，请检查元素是否正确对应</li>
                    <li><strong>已删除元素</strong>: 请确认元素是否真的从页面移除，还是定位器失效</li>
                </ul>
            </div>
        </div>
'''
        
        html = f'''<!DOCTYPE html>
<html lang="zh">
<head>
    <meta charset="UTF-8">
    <title>页面变更检测报告 - {class_name}</title>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
            color: #e0e0e0;
            min-height: 100vh;
            padding: 2rem;
        }}
        .container {{ max-width: 1600px; margin: 0 auto; }}
        
        /* 头部 */
        .header {{
            background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
            border-radius: 16px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            border: 1px solid rgba(233, 69, 96, 0.2);
        }}
        h1 {{ 
            color: #e94560; 
            font-size: 2.2rem; 
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        .meta {{ 
            color: #a0a0a0; 
            font-size: 0.9rem;
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
        }}
        .meta strong {{ color: #e0e0e0; }}
        
        /* 可靠性评分卡 */
        .reliability-card {{
            background: linear-gradient(135deg, rgba(0,0,0,0.3), rgba(0,0,0,0.1));
            border-radius: 12px;
            padding: 1.5rem;
            margin-top: 1.5rem;
            display: flex;
            align-items: center;
            gap: 2rem;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        .reliability-score {{
            font-size: 3rem;
            font-weight: bold;
            color: {reliability_color};
        }}
        .reliability-info h3 {{
            color: {reliability_color};
            margin-bottom: 0.5rem;
        }}
        .reliability-info p {{
            color: #a0a0a0;
            font-size: 0.9rem;
        }}
        
        /* 警告横幅 */
        .warning-banner {{
            background: linear-gradient(135deg, rgba(244, 67, 54, 0.15), rgba(255, 152, 0, 0.1));
            border: 2px solid #f44336;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            gap: 1.5rem;
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{
            0%, 100% {{ border-color: #f44336; }}
            50% {{ border-color: #ff9800; }}
        }}
        .warning-icon {{
            font-size: 2.5rem;
        }}
        .warning-content h3 {{
            color: #f44336;
            margin-bottom: 0.5rem;
        }}
        .warning-content p {{
            color: #a0a0a0;
            margin-bottom: 0.5rem;
        }}
        .warning-content ul {{
            margin-left: 1.5rem;
            color: #a0a0a0;
            font-size: 0.9rem;
        }}
        
        /* 统计卡片 */
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        .stat-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }}
        .stat-card .number {{ 
            font-size: 2.2rem; 
            font-weight: bold; 
        }}
        .stat-card .label {{ 
            color: #808080; 
            font-size: 0.85rem; 
            margin-top: 0.5rem; 
        }}
        .stat-card.modified .number {{ color: #ffc107; }}
        .stat-card.added .number {{ color: #4caf50; }}
        .stat-card.deleted .number {{ color: #f44336; }}
        .stat-card.unchanged .number {{ color: #2196f3; }}
        
        /* 置信度统计卡片 */
        .conf-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        .conf-stat-card {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1.2rem;
            display: flex;
            align-items: center;
            gap: 1rem;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        .conf-stat-card .icon {{ font-size: 2rem; }}
        .conf-stat-card .info .number {{ font-size: 1.8rem; font-weight: bold; }}
        .conf-stat-card .info .label {{ color: #808080; font-size: 0.8rem; }}
        .conf-stat-card.high .number {{ color: #4caf50; }}
        .conf-stat-card.medium .number {{ color: #ffc107; }}
        .conf-stat-card.low .number {{ color: #f44336; }}
        
        /* 图例 */
        .legend {{
            background: rgba(255,255,255,0.03);
            border-radius: 12px;
            padding: 1rem 1.5rem;
            margin-bottom: 2rem;
            display: flex;
            flex-wrap: wrap;
            gap: 2rem;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        .legend-section {{
            display: flex;
            align-items: center;
            gap: 1.5rem;
        }}
        .legend-title {{
            color: #808080;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .legend-items {{
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.85rem;
        }}
        
        /* 表格 */
        .changes-table {{
            background: rgba(255,255,255,0.02);
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid rgba(255,255,255,0.08);
            box-shadow: 0 4px 20px rgba(0,0,0,0.2);
        }}
        table {{ 
            width: 100%; 
            border-collapse: collapse; 
        }}
        th {{
            background: rgba(233, 69, 96, 0.15);
            padding: 1rem;
            text-align: left;
            font-weight: 600;
            color: #e94560;
            position: sticky;
            top: 0;
        }}
        td {{
            padding: 1rem;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            vertical-align: top;
        }}
        tr:hover {{ 
            background: rgba(255,255,255,0.03); 
        }}
        tr.modified {{ background: rgba(255, 193, 7, 0.08); }}
        tr.added {{ background: rgba(76, 175, 80, 0.08); }}
        tr.deleted {{ background: rgba(244, 67, 54, 0.08); }}
        tr.needs-review {{
            border-left: 4px solid #f44336;
        }}
        
        /* 单元格样式 */
        .status-cell {{ 
            width: 50px; 
            text-align: center; 
            font-size: 1.2rem;
        }}
        .method-cell {{ width: 200px; }}
        .locator-cell {{ max-width: 300px; }}
        .reason-cell {{ width: 200px; color: #a0a0a0; }}
        .conf-cell {{ 
            width: 120px; 
            text-align: center;
        }}
        
        /* 代码样式 */
        code {{
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.8rem;
            background: rgba(0,0,0,0.4);
            padding: 0.3rem 0.6rem;
            border-radius: 6px;
            word-break: break-all;
            display: inline-block;
            max-width: 100%;
        }}
        code.old {{ 
            color: #ff6b6b;
            text-decoration: line-through;
            opacity: 0.8;
        }}
        code.new {{ 
            color: #69db7c;
        }}
        
        /* 置信度徽章 */
        .conf-badge {{
            display: inline-block;
            padding: 0.3rem 0.6rem;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.85rem;
        }}
        .conf-label {{
            display: block;
            font-size: 0.75rem;
            color: #808080;
            margin-top: 0.3rem;
        }}
        .conf-high .conf-badge {{
            background: rgba(76, 175, 80, 0.2);
            color: #4caf50;
        }}
        .conf-medium .conf-badge {{
            background: rgba(255, 193, 7, 0.2);
            color: #ffc107;
        }}
        .conf-low .conf-badge {{
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
        }}
        
        /* 需要确认徽章 */
        .review-badge {{
            display: inline-block;
            background: linear-gradient(135deg, #f44336, #ff9800);
            color: white;
            padding: 0.2rem 0.5rem;
            border-radius: 4px;
            font-size: 0.7rem;
            font-weight: bold;
            margin-left: 0.5rem;
            animation: blink 1.5s infinite;
        }}
        @keyframes blink {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        /* 页脚 */
        .footer {{
            margin-top: 2rem;
            text-align: center;
            color: #505050;
            font-size: 0.85rem;
            padding: 1rem;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 页面变更检测报告</h1>
            <div class="meta">
                <span><strong>PageObject:</strong> {class_name}</span>
                <span><strong>URL:</strong> {url}</span>
                <span><strong>检测时间:</strong> {timestamp}</span>
            </div>
            <div class="reliability-card">
                <div class="reliability-score">{reliability_score:.0f}%</div>
                <div class="reliability-info">
                    <h3>匹配可靠性: {reliability_label}</h3>
                    <p>基于代码分析的置信度评估。高置信度匹配可直接使用，低置信度匹配建议人工确认。</p>
                </div>
            </div>
        </div>
        
        {warning_section}
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{total}</div>
                <div class="label">总元素</div>
            </div>
            <div class="stat-card unchanged">
                <div class="number">{unchanged}</div>
                <div class="label">未变更</div>
            </div>
            <div class="stat-card modified">
                <div class="number">{modified}</div>
                <div class="label">已修改</div>
            </div>
            <div class="stat-card added">
                <div class="number">{added}</div>
                <div class="label">新增</div>
            </div>
            <div class="stat-card deleted">
                <div class="number">{deleted}</div>
                <div class="label">已删除</div>
            </div>
        </div>
        
        <div class="conf-stats">
            <div class="conf-stat-card high">
                <div class="icon">🟢</div>
                <div class="info">
                    <div class="number">{high_conf}</div>
                    <div class="label">高置信度 (≥90%) - 纯代码可靠</div>
                </div>
            </div>
            <div class="conf-stat-card medium">
                <div class="icon">🟡</div>
                <div class="info">
                    <div class="number">{medium_conf}</div>
                    <div class="label">中置信度 (60-89%) - 代码较可靠</div>
                </div>
            </div>
            <div class="conf-stat-card low">
                <div class="icon">🔴</div>
                <div class="info">
                    <div class="number">{low_conf}</div>
                    <div class="label">低置信度 (&lt;60%) - 需人工确认</div>
                </div>
            </div>
        </div>
        
        <div class="legend">
            <div class="legend-section">
                <span class="legend-title">变更类型:</span>
                <div class="legend-items">
                    <span class="legend-item">✅ 未变更</span>
                    <span class="legend-item">🔄 已修改</span>
                    <span class="legend-item">➕ 新增</span>
                    <span class="legend-item">❌ 已删除</span>
                </div>
            </div>
            <div class="legend-section">
                <span class="legend-title">置信度:</span>
                <div class="legend-items">
                    <span class="legend-item">🟢 高 (data-testid/ID精确匹配)</span>
                    <span class="legend-item">🟡 中 (文本+属性组合)</span>
                    <span class="legend-item">🔴 低 (模糊匹配)</span>
                </div>
            </div>
        </div>
        
        <div class="changes-table">
            <table>
                <thead>
                    <tr>
                        <th style="width: 50px">状态</th>
                        <th style="width: 200px">方法名</th>
                        <th>旧定位器</th>
                        <th>新定位器</th>
                        <th style="width: 200px">变更原因</th>
                        <th style="width: 120px">置信度</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(change_rows)}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Generated by UI Java Agent - Page Change Detector | 分层匹配策略: 高置信度(纯代码) → 中置信度(规则) → 低置信度(需确认)
        </div>
    </div>
</body>
</html>'''
        
        return html
    
    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        if not text:
            return text
        return (text
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;')
            .replace("'", '&#39;'))


def detect_page_changes(
    old_page_code: str,
    snapshot_data: str,
    url: str = "",
    workspace_path: Path = None
) -> dict:
    """
    检测页面变更的便捷函数
    
    Args:
        old_page_code: 旧的 PageObject Java 代码
        snapshot_data: Playwright MCP browser_snapshot 返回的数据
        url: 页面 URL
        workspace_path: 工作区路径
    
    Returns:
        {
            'class_name': str,
            'changes': List[LocatorChange],
            'new_page_code': str,
            'html_report': str,
            'summary': dict
        }
    """
    # 解析旧代码获取类名
    class_name, _ = PageObjectParser.parse(old_page_code)
    
    # 解析当前页面元素
    elements = PlaywrightMCPElementParser.parse_snapshot(snapshot_data)
    
    # 检测变更
    detector = PageChangeDetector(workspace_path)
    changes = detector.detect_changes(old_page_code, elements)
    
    # 生成输出
    new_page_code = detector.generate_new_page_object(class_name, changes, url)
    html_report = detector.generate_html_report(class_name, changes, url)
    
    # 统计摘要
    summary = {
        'total': len(changes),
        'unchanged': sum(1 for c in changes if c.change_type == ChangeType.UNCHANGED),
        'modified': sum(1 for c in changes if c.change_type == ChangeType.MODIFIED),
        'added': sum(1 for c in changes if c.change_type == ChangeType.ADDED),
        'deleted': sum(1 for c in changes if c.change_type == ChangeType.DELETED),
    }
    
    return {
        'class_name': class_name,
        'changes': changes,
        'new_page_code': new_page_code,
        'html_report': html_report,
        'summary': summary
    }
