"""
智能定位器优化器 - 真实浏览器验证版本

核心改进：
1. ✅ 真实浏览器中验证优化后的定位器
2. ✅ 多种定位策略稳定性评分
3. ✅ 支持定位器变化检测
4. ✅ 自动生成多个候选定位器并选择最优
5. ✅ 生成可视化对比报告
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from playwright.sync_api import sync_playwright, Page, Locator
from .locator_diff_reporter import LocatorDiffReporter, LocatorChange


@dataclass
class LocatorStrategy:
    """定位器策略"""
    locator: str  # 定位器表达式
    strategy_type: str  # 策略类型：data-testid/id/aria/text/css
    stability_score: float  # 稳定性评分 (0-100)
    uniqueness: bool  # 是否唯一定位
    element_count: int  # 匹配到的元素数量
    is_visible: bool  # 元素是否可见
    performance_ms: float  # 定位耗时（毫秒）


@dataclass
class LocatorOptimization:
    """定位器优化结果"""
    original: str
    optimized: str
    strategy: LocatorStrategy
    alternatives: List[LocatorStrategy]  # 备选方案
    confidence: float
    reason: str
    verified: bool  # 是否在真实浏览器中验证过


class SmartLocatorOptimizer:
    """
    智能定位器优化器
    
    特点：
    - 在真实浏览器中验证每个定位器
    - 评估定位器的稳定性、唯一性、可见性
    - 生成多个候选方案
    - 选择最优定位策略
    """
    
    # 稳定性评分权重
    STABILITY_WEIGHTS = {
        'data-testid': 100,  # 最稳定
        'id': 95,
        'name': 90,
        'aria-label': 85,
        'placeholder': 80,
        'role': 75,
        'text': 70,
        'class': 40,  # 较不稳定
        'nth-child': 20,  # 很不稳定
        'css-complex': 30,  # 复杂CSS
    }
    
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
    
    def __enter__(self):
        """上下文管理器入口"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=self.headless)
        self.context = self.browser.new_context(viewport={'width': 1920, 'height': 1080})
        self.page = self.context.new_page()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        if self.page:
            self.page.close()
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
    
    def navigate(self, url: str, storage_state: str = None):
        """
        导航到目标页面
        
        Args:
            url: 目标URL
            storage_state: 认证状态文件路径
        """
        if storage_state:
            # 重新创建带认证的 context
            if self.context:
                self.context.close()
            self.context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                storage_state=storage_state
            )
            if self.page:
                self.page.close()
            self.page = self.context.new_page()
        
        self.page.goto(url, wait_until='networkidle', timeout=60000)
        self.page.wait_for_timeout(2000)  # 等待动态内容加载
    
    def is_fragile_locator(self, locator: str) -> bool:
        """检查定位器是否脆弱"""
        fragile_patterns = [
            r'nth-child\(\d+\)',
            r'nth-of-type\(\d+\)',
            r'>> nth=',
            r'\[class\*="[^"]*\d+[^"]*"\]',  # 动态class
            r'div > div > div > ',  # 过深的层级
        ]
        
        for pattern in fragile_patterns:
            if re.search(pattern, locator):
                return True
        return False
    
    def generate_locator_strategies(self, element_handle) -> List[LocatorStrategy]:
        """
        为元素生成多种定位策略并评估
        
        Args:
            element_handle: Playwright元素句柄
        
        Returns:
            按稳定性评分排序的定位策略列表
        """
        strategies = []
        
        try:
            # 1. data-testid（最优）
            testid = element_handle.get_attribute('data-testid')
            if testid:
                strategy = self._evaluate_strategy(
                    locator=f'[data-testid="{testid}"]',
                    strategy_type='data-testid'
                )
                if strategy:
                    strategies.append(strategy)
            
            # 2. id
            elem_id = element_handle.get_attribute('id')
            if elem_id and not re.search(r'\d{5,}', elem_id):  # 避免动态ID
                strategy = self._evaluate_strategy(
                    locator=f'#{elem_id}',
                    strategy_type='id'
                )
                if strategy:
                    strategies.append(strategy)
            
            # 3. name
            name = element_handle.get_attribute('name')
            if name:
                strategy = self._evaluate_strategy(
                    locator=f'[name="{name}"]',
                    strategy_type='name'
                )
                if strategy:
                    strategies.append(strategy)
            
            # 4. aria-label
            aria_label = element_handle.get_attribute('aria-label')
            if aria_label:
                strategy = self._evaluate_strategy(
                    locator=f'[aria-label="{aria_label}"]',
                    strategy_type='aria-label'
                )
                if strategy:
                    strategies.append(strategy)
            
            # 5. placeholder（for input）
            placeholder = element_handle.get_attribute('placeholder')
            if placeholder:
                strategy = self._evaluate_strategy(
                    locator=f'[placeholder="{placeholder}"]',
                    strategy_type='placeholder'
                )
                if strategy:
                    strategies.append(strategy)
            
            # 6. role + name（getByRole方式）
            role = element_handle.get_attribute('role') or self._infer_role(element_handle)
            if role:
                text = element_handle.text_content()
                if text and text.strip():
                    # 构造 getByRole 等价的 CSS
                    strategy = self._evaluate_strategy(
                        locator=f'[role="{role}"]',
                        strategy_type='role'
                    )
                    if strategy:
                        strategies.append(strategy)
            
            # 7. 文本定位
            text = element_handle.text_content()
            if text and text.strip() and len(text.strip()) < 50:
                # 使用 text= 选择器
                text_clean = text.strip().replace('"', '\\"')
                strategy = self._evaluate_strategy(
                    locator=f'text="{text_clean}"',
                    strategy_type='text'
                )
                if strategy:
                    strategies.append(strategy)
            
        except Exception as e:
            print(f"⚠️  生成定位策略时出错: {e}")
        
        # 按稳定性评分排序
        strategies.sort(key=lambda s: s.stability_score, reverse=True)
        
        return strategies
    
    def _infer_role(self, element_handle) -> Optional[str]:
        """推断元素的 ARIA role"""
        tag = element_handle.evaluate('el => el.tagName').lower()
        
        role_map = {
            'button': 'button',
            'a': 'link',
            'input': 'textbox',
            'select': 'combobox',
            'textarea': 'textbox',
            'img': 'img',
            'nav': 'navigation',
            'header': 'banner',
            'footer': 'contentinfo',
        }
        
        return role_map.get(tag)
    
    def _evaluate_strategy(self, locator: str, strategy_type: str) -> Optional[LocatorStrategy]:
        """
        评估定位策略的有效性
        
        Returns:
            LocatorStrategy 如果有效，否则 None
        """
        import time
        
        try:
            start_time = time.time()
            
            # 尝试定位
            loc = self.page.locator(locator)
            count = loc.count()
            
            if count == 0:
                return None  # 找不到元素
            
            # 检查第一个元素的可见性
            is_visible = False
            if count > 0:
                try:
                    is_visible = loc.first.is_visible()
                except:
                    pass
            
            performance_ms = (time.time() - start_time) * 1000
            
            # 计算稳定性评分
            base_score = self.STABILITY_WEIGHTS.get(strategy_type, 50)
            
            # 唯一性加分
            uniqueness_bonus = 20 if count == 1 else 0
            
            # 可见性加分
            visibility_bonus = 10 if is_visible else 0
            
            # 性能加分（快速定位）
            performance_bonus = 5 if performance_ms < 100 else 0
            
            stability_score = min(100, base_score + uniqueness_bonus + visibility_bonus + performance_bonus)
            
            return LocatorStrategy(
                locator=locator,
                strategy_type=strategy_type,
                stability_score=stability_score,
                uniqueness=(count == 1),
                element_count=count,
                is_visible=is_visible,
                performance_ms=performance_ms
            )
        
        except Exception as e:
            return None
    
    def find_element_by_fragile_locator(self, fragile_locator: str):
        """
        使用脆弱定位器找到元素（用于后续分析）
        
        Returns:
            元素句柄，如果找不到返回 None
        """
        try:
            loc = self.page.locator(fragile_locator)
            if loc.count() > 0:
                return loc.first.element_handle()
        except:
            pass
        
        return None
    
    def optimize_locator(self, original_locator: str) -> Optional[LocatorOptimization]:
        """
        优化单个定位器
        
        Args:
            original_locator: 原始定位器
        
        Returns:
            优化结果，如果无法优化返回 None
        """
        # 检查是否需要优化
        if not self.is_fragile_locator(original_locator):
            return None
        
        # 使用原始定位器找到元素
        element = self.find_element_by_fragile_locator(original_locator)
        if not element:
            print(f"⚠️  无法定位元素: {original_locator}")
            return None
        
        # 生成多种定位策略
        strategies = self.generate_locator_strategies(element)
        
        if not strategies:
            print(f"⚠️  无法生成优化策略: {original_locator}")
            return None
        
        # 选择最优策略
        best_strategy = strategies[0]
        alternatives = strategies[1:4]  # 保留前3个备选方案
        
        # 计算置信度
        confidence = best_strategy.stability_score / 100.0
        
        # 生成原因说明
        reason = f"使用 {best_strategy.strategy_type} 策略（稳定性: {best_strategy.stability_score:.0f}分"
        if best_strategy.uniqueness:
            reason += ", 唯一定位"
        else:
            reason += f", {best_strategy.element_count}个匹配"
        reason += "）"
        
        return LocatorOptimization(
            original=original_locator,
            optimized=best_strategy.locator,
            strategy=best_strategy,
            alternatives=alternatives,
            confidence=confidence,
            reason=reason,
            verified=True
        )
    
    def optimize_code(self, code: str, url: str, language: str = 'java',
                     storage_state: str = None, generate_report: bool = True,
                     file_path: str = None) -> Tuple[str, List[LocatorOptimization], str]:
        """
        优化代码中的所有定位器
        
        Args:
            code: 原始代码
            url: 目标页面URL
            language: 代码语言
            storage_state: 认证状态文件
            generate_report: 是否生成HTML报告
            file_path: 文件路径（用于报告）
        
        Returns:
            (优化后的代码, 优化记录列表, 报告文件路径)
        """
        # 导航到目标页面
        self.navigate(url, storage_state)
        
        # 提取定位器
        locators = self._extract_locators(code, language)
        
        optimizations = []
        optimized_code = code
        
        print(f"\n🔍 分析页面: {url}")
        print(f"📝 找到 {len(locators)} 个定位器")
        
        # 优化每个定位器
        for i, (original_line, locator) in enumerate(locators, 1):
            print(f"\n[{i}/{len(locators)}] 处理: {locator[:60]}...")
            
            optimization = self.optimize_locator(locator)
            
            if optimization:
                # 替换代码中的定位器
                new_line = self._replace_locator_in_line(
                    original_line, locator, optimization.optimized, language
                )
                optimized_code = optimized_code.replace(original_line, new_line)
                optimizations.append(optimization)
                
                print(f"  ✅ {optimization.optimized} ({optimization.strategy.stability_score:.0f}分)")
            else:
                print(f"  ⏭️  跳过（已是稳定定位器或无法优化）")
        
        # 生成报告
        report_path = None
        if generate_report and optimizations:
            reporter = LocatorDiffReporter()
            
            # 添加变化记录
            for opt in optimizations:
                change = LocatorChange(
                    line_number=0,  # 可以改进为实际行号
                    original_locator=opt.original,
                    optimized_locator=opt.optimized,
                    strategy_type=opt.strategy.strategy_type,
                    stability_score=opt.strategy.stability_score,
                    confidence=opt.confidence,
                    reason=opt.reason,
                    alternatives=[alt.locator for alt in opt.alternatives]
                )
                reporter.add_change(change)
            
            # 生成HTML报告
            report_path = reporter.generate_html_report(
                original_code=code,
                optimized_code=optimized_code,
                file_path=file_path or 'unknown',
                page_url=url,
                language=language
            )
            
            if report_path:
                print(f"\n📊 HTML对比报告已生成: {report_path}")
        
        return optimized_code, optimizations, report_path
    
    def _extract_locators(self, code: str, language: str) -> List[Tuple[str, str]]:
        """提取代码中的定位器"""
        locators = []
        
        if language == 'java':
            patterns = [
                r'page\.locator\("([^"]+)"\)',
                r'page\.getByRole\([^,]+,\s*new\s+Page\.GetByRoleOptions\(\)\.setName\("([^"]+)"\)\)',
            ]
        else:  # python
            patterns = [
                r'page\.locator\(["\']([^"\']+)["\']\)',
            ]
        
        for line in code.split('\n'):
            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    locators.append((line.strip(), match.group(1)))
        
        return locators
    
    def _replace_locator_in_line(self, line: str, old_locator: str, new_locator: str, language: str) -> str:
        """替换代码行中的定位器"""
        if language == 'java':
            # Java: page.locator("old") -> page.locator("new")
            return line.replace(f'"{old_locator}"', f'"{new_locator}"')
        else:  # python
            # Python: page.locator("old") -> page.locator("new")
            return line.replace(f'"{old_locator}"', f'"{new_locator}"').replace(f"'{old_locator}'", f"'{new_locator}'")
    
    def detect_locator_changes(self, test_code: str, url: str, language: str = 'java',
                               storage_state: str = None) -> Dict[str, any]:
        """
        检测定位器是否失效（用于维护场景）
        
        Args:
            test_code: 测试代码
            url: 目标URL
            language: 代码语言
            storage_state: 认证状态
        
        Returns:
            {
                'total': 总定位器数,
                'valid': 有效数,
                'invalid': 失效数,
                'failed_locators': [失效的定位器列表],
                'suggestions': {locator: [建议的替代方案]}
            }
        """
        self.navigate(url, storage_state)
        
        locators = self._extract_locators(test_code, language)
        
        result = {
            'total': len(locators),
            'valid': 0,
            'invalid': 0,
            'failed_locators': [],
            'suggestions': {}
        }
        
        print(f"\n🔍 检测定位器有效性...")
        
        for line, locator in locators:
            try:
                loc = self.page.locator(locator)
                count = loc.count()
                
                if count > 0:
                    result['valid'] += 1
                    print(f"  ✅ {locator[:50]}... ({count} 个匹配)")
                else:
                    result['invalid'] += 1
                    result['failed_locators'].append(locator)
                    print(f"  ❌ {locator[:50]}... (找不到元素)")
                    
                    # TODO: 尝试生成替代建议
                    # 这里可以基于页面当前元素生成建议
                    
            except Exception as e:
                result['invalid'] += 1
                result['failed_locators'].append(locator)
                print(f"  ❌ {locator[:50]}... (错误: {e})")
        
        print(f"\n📊 检测完成: {result['valid']}/{result['total']} 个定位器有效")
        
        return result


def print_optimization_report(optimizations: List[LocatorOptimization]):
    """打印优化报告"""
    if not optimizations:
        print("\n✅ 所有定位器已经很稳定，无需优化")
        return
    
    print("\n" + "=" * 70)
    print(f"🔧 定位器优化报告 - 共优化 {len(optimizations)} 个定位器")
    print("=" * 70)
    
    for i, opt in enumerate(optimizations, 1):
        print(f"\n{i}. 置信度: {opt.confidence*100:.0f}% | 稳定性: {opt.strategy.stability_score:.0f}分")
        print(f"   策略: {opt.strategy.strategy_type}")
        print(f"   原始: {opt.original}")
        print(f"   优化: {opt.optimized}")
        print(f"   说明: {opt.reason}")
        
        if opt.alternatives:
            print(f"   备选方案:")
            for j, alt in enumerate(opt.alternatives[:2], 1):
                print(f"     {j}) {alt.locator} ({alt.stability_score:.0f}分)")
    
    print("\n" + "=" * 70)
