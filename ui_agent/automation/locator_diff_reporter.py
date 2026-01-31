"""
定位器优化对比报告生成器

功能：
- 生成 HTML 可视化对比报告
- 展示优化前后的代码 diff
- 列出每个定位器的变化详情
- 便于维护和审查
"""

import difflib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class LocatorChange:
    """定位器变化记录"""
    line_number: int
    original_locator: str
    optimized_locator: str
    strategy_type: str
    stability_score: float
    confidence: float
    reason: str
    alternatives: List[str]


class LocatorDiffReporter:
    """定位器优化对比报告生成器"""
    
    HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>定位器优化对比报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #f5f7fa;
            padding: 20px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px 40px;
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 10px;
        }}
        
        .header .meta {{
            opacity: 0.9;
            font-size: 14px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .summary-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        
        .summary-card .label {{
            color: #6c757d;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 8px;
        }}
        
        .summary-card .value {{
            font-size: 24px;
            font-weight: bold;
            color: #2d3748;
        }}
        
        .summary-card.success {{
            border-left-color: #10b981;
        }}
        
        .summary-card.warning {{
            border-left-color: #f59e0b;
        }}
        
        .summary-card.info {{
            border-left-color: #3b82f6;
        }}
        
        .section {{
            padding: 30px 40px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .section h2 {{
            font-size: 20px;
            color: #2d3748;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
        }}
        
        .section h2::before {{
            content: '';
            width: 4px;
            height: 20px;
            background: #667eea;
            margin-right: 12px;
            border-radius: 2px;
        }}
        
        /* 代码对比 */
        .code-diff {{
            background: #1e1e1e;
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 20px;
        }}
        
        .diff-header {{
            background: #2d2d30;
            padding: 12px 20px;
            color: #ccc;
            font-size: 13px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .diff-tabs {{
            display: flex;
            gap: 10px;
        }}
        
        .diff-tab {{
            padding: 6px 12px;
            background: #3e3e42;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .diff-tab.active {{
            background: #667eea;
        }}
        
        .diff-content {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0;
            max-height: 600px;
            overflow-y: auto;
        }}
        
        .diff-pane {{
            background: #1e1e1e;
            padding: 0;
        }}
        
        .diff-pane-header {{
            background: #2d2d30;
            padding: 8px 16px;
            color: #fff;
            font-size: 12px;
            font-weight: 600;
            border-bottom: 1px solid #3e3e42;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        .diff-pane-header.before {{
            background: #7f1d1d;
        }}
        
        .diff-pane-header.after {{
            background: #14532d;
        }}
        
        pre {{
            margin: 0;
            padding: 16px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 13px;
            line-height: 1.5;
            color: #d4d4d4;
            white-space: pre-wrap;
            word-break: break-all;
        }}
        
        .diff-line {{
            display: block;
            padding: 2px 8px;
            margin: 0 -8px;
        }}
        
        .diff-line.removed {{
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
        }}
        
        .diff-line.added {{
            background: rgba(34, 197, 94, 0.2);
            color: #86efac;
        }}
        
        .diff-line.unchanged {{
            color: #a8a8a8;
        }}
        
        /* 变化列表 */
        .changes-list {{
            display: flex;
            flex-direction: column;
            gap: 16px;
        }}
        
        .change-card {{
            background: #f8f9fa;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #667eea;
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .change-card:hover {{
            transform: translateX(4px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        
        .change-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        
        .change-number {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .change-score {{
            display: flex;
            gap: 12px;
            align-items: center;
        }}
        
        .score-badge {{
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .score-badge.excellent {{
            background: #d1fae5;
            color: #065f46;
        }}
        
        .score-badge.good {{
            background: #dbeafe;
            color: #1e40af;
        }}
        
        .score-badge.medium {{
            background: #fef3c7;
            color: #92400e;
        }}
        
        .locator-compare {{
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 12px;
            align-items: center;
            margin: 12px 0;
            padding: 12px;
            background: white;
            border-radius: 6px;
        }}
        
        .locator-box {{
            padding: 8px 12px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 13px;
        }}
        
        .locator-box.before {{
            background: #fee2e2;
            color: #991b1b;
            border: 1px solid #fca5a5;
        }}
        
        .locator-box.after {{
            background: #dcfce7;
            color: #14532d;
            border: 1px solid #86efac;
        }}
        
        .arrow {{
            color: #667eea;
            font-size: 20px;
            font-weight: bold;
        }}
        
        .change-details {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 12px;
            margin-top: 12px;
        }}
        
        .detail-item {{
            padding: 8px 12px;
            background: white;
            border-radius: 4px;
            font-size: 13px;
        }}
        
        .detail-label {{
            color: #6c757d;
            font-size: 11px;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        
        .detail-value {{
            color: #2d3748;
            font-weight: 600;
        }}
        
        .alternatives {{
            margin-top: 12px;
            padding: 12px;
            background: #fff7ed;
            border-radius: 6px;
            border-left: 3px solid #f59e0b;
        }}
        
        .alternatives-title {{
            color: #92400e;
            font-size: 12px;
            font-weight: 600;
            margin-bottom: 8px;
        }}
        
        .alternatives-list {{
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}
        
        .alternative-item {{
            padding: 6px 10px;
            background: white;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .alternative-score {{
            color: #667eea;
            font-weight: 600;
        }}
        
        /* 工具栏 */
        .toolbar {{
            padding: 20px 40px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .btn {{
            padding: 10px 20px;
            border-radius: 6px;
            border: none;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.2s;
        }}
        
        .btn-primary {{
            background: #667eea;
            color: white;
        }}
        
        .btn-primary:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
        }}
        
        .btn-secondary {{
            background: white;
            color: #667eea;
            border: 1px solid #667eea;
        }}
        
        .btn-secondary:hover {{
            background: #f0f1ff;
        }}
        
        /* 响应式 */
        @media (max-width: 768px) {{
            .diff-content {{
                grid-template-columns: 1fr;
            }}
            
            .locator-compare {{
                grid-template-columns: 1fr;
            }}
            
            .arrow {{
                transform: rotate(90deg);
            }}
        }}
        
        /* 滚动条样式 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: #2d2d30;
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: #667eea;
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部 -->
        <div class="header">
            <h1>🔍 定位器优化对比报告</h1>
            <div class="meta">
                <div>📁 文件: {file_name}</div>
                <div>🌐 页面: {page_url}</div>
                <div>📅 生成时间: {timestamp}</div>
            </div>
        </div>
        
        <!-- 统计摘要 -->
        <div class="summary">
            <div class="summary-card success">
                <div class="label">优化定位器数量</div>
                <div class="value">{optimized_count}</div>
            </div>
            <div class="summary-card info">
                <div class="label">平均稳定性评分</div>
                <div class="value">{avg_stability:.0f}分</div>
            </div>
            <div class="summary-card warning">
                <div class="label">平均置信度</div>
                <div class="value">{avg_confidence:.0f}%</div>
            </div>
            <div class="summary-card">
                <div class="label">代码语言</div>
                <div class="value">{language}</div>
            </div>
        </div>
        
        <!-- 代码对比 -->
        <div class="section">
            <h2>📝 代码对比</h2>
            <div class="code-diff">
                <div class="diff-header">
                    <span>Side-by-Side Diff</span>
                    <div class="diff-tabs">
                        <div class="diff-tab active">完整对比</div>
                    </div>
                </div>
                <div class="diff-content">
                    <div class="diff-pane">
                        <div class="diff-pane-header before">❌ 优化前 (Original)</div>
                        <pre>{code_before_html}</pre>
                    </div>
                    <div class="diff-pane">
                        <div class="diff-pane-header after">✅ 优化后 (Optimized)</div>
                        <pre>{code_after_html}</pre>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- 详细变化列表 -->
        <div class="section">
            <h2>🔧 定位器变化详情</h2>
            <div class="changes-list">
                {changes_html}
            </div>
        </div>
        
        <!-- 工具栏 -->
        <div class="toolbar">
            <div>
                <button class="btn btn-secondary" onclick="window.print()">🖨️ 打印报告</button>
            </div>
            <div>
                <button class="btn btn-primary" onclick="window.close()">✓ 完成</button>
            </div>
        </div>
    </div>
    
    <script>
        // 代码高亮
        document.querySelectorAll('pre').forEach(block => {{
            // 简单的语法高亮可以在这里添加
        }});
    </script>
</body>
</html>
"""
    
    CHANGE_CARD_TEMPLATE = """
                <div class="change-card">
                    <div class="change-header">
                        <div class="change-number">变更 #{number}</div>
                        <div class="change-score">
                            <span class="score-badge {score_class}">稳定性 {stability_score:.0f}分</span>
                            <span class="score-badge {confidence_class}">置信度 {confidence:.0f}%</span>
                        </div>
                    </div>
                    
                    <div class="locator-compare">
                        <div class="locator-box before">
                            {original_locator}
                        </div>
                        <div class="arrow">→</div>
                        <div class="locator-box after">
                            {optimized_locator}
                        </div>
                    </div>
                    
                    <div class="change-details">
                        <div class="detail-item">
                            <div class="detail-label">策略类型</div>
                            <div class="detail-value">{strategy_type}</div>
                        </div>
                        <div class="detail-item">
                            <div class="detail-label">优化原因</div>
                            <div class="detail-value">{reason}</div>
                        </div>
                    </div>
                    
                    {alternatives_html}
                </div>
"""
    
    def __init__(self):
        self.changes: List[LocatorChange] = []
    
    def add_change(self, change: LocatorChange):
        """添加变化记录"""
        self.changes.append(change)
    
    def generate_html_report(
        self,
        original_code: str,
        optimized_code: str,
        file_path: str,
        page_url: str,
        language: str,
        output_path: str = None
    ) -> str:
        """
        生成 HTML 对比报告
        
        Args:
            original_code: 原始代码
            optimized_code: 优化后的代码
            file_path: 文件路径
            page_url: 页面URL
            language: 代码语言
            output_path: 输出路径（默认自动生成）
        
        Returns:
            生成的报告文件路径
        """
        if not self.changes:
            return None
        
        # 计算统计数据
        optimized_count = len(self.changes)
        avg_stability = sum(c.stability_score for c in self.changes) / optimized_count
        avg_confidence = sum(c.confidence for c in self.changes) / optimized_count * 100
        
        # 生成代码 diff HTML
        code_before_html = self._highlight_code(original_code, optimized_code, is_before=True)
        code_after_html = self._highlight_code(optimized_code, original_code, is_before=False)
        
        # 生成变化列表 HTML
        changes_html = self._generate_changes_html()
        
        # 填充模板
        html_content = self.HTML_TEMPLATE.format(
            file_name=Path(file_path).name,
            page_url=page_url,
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            optimized_count=optimized_count,
            avg_stability=avg_stability,
            avg_confidence=avg_confidence,
            language=language.upper(),
            code_before_html=code_before_html,
            code_after_html=code_after_html,
            changes_html=changes_html
        )
        
        # 确定输出路径
        if not output_path:
            output_dir = Path('./output/reports')
            output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = output_dir / f'locator_optimization_{timestamp}.html'
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(output_path)
    
    def _highlight_code(self, code: str, other_code: str, is_before: bool) -> str:
        """
        高亮代码差异
        
        Args:
            code: 当前代码
            other_code: 对比代码
            is_before: 是否是优化前的代码
        """
        lines1 = code.splitlines()
        lines2 = other_code.splitlines()
        
        # 使用 difflib 生成 diff
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        
        html_lines = []
        for tag, i1, i2, j1, j2 in matcher.get_opcodes():
            if tag == 'equal':
                # 未改变的行
                for i in range(i1, i2):
                    line = self._escape_html(lines1[i])
                    html_lines.append(f'<span class="diff-line unchanged">{i+1:4d} │ {line}</span>')
            
            elif tag == 'delete' and is_before:
                # 删除的行（仅在 before 显示）
                for i in range(i1, i2):
                    line = self._escape_html(lines1[i])
                    html_lines.append(f'<span class="diff-line removed">{i+1:4d} │ {line}</span>')
            
            elif tag == 'insert' and not is_before:
                # 插入的行（仅在 after 显示）
                for j in range(j1, j2):
                    line = self._escape_html(lines2[j])
                    html_lines.append(f'<span class="diff-line added">{j+1:4d} │ {line}</span>')
            
            elif tag == 'replace':
                if is_before:
                    # 显示被替换的行
                    for i in range(i1, i2):
                        line = self._escape_html(lines1[i])
                        html_lines.append(f'<span class="diff-line removed">{i+1:4d} │ {line}</span>')
                else:
                    # 显示替换后的行
                    for j in range(j1, j2):
                        line = self._escape_html(lines2[j])
                        html_lines.append(f'<span class="diff-line added">{j+1:4d} │ {line}</span>')
        
        return '\n'.join(html_lines)
    
    def _escape_html(self, text: str) -> str:
        """转义 HTML 特殊字符"""
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#39;'))
    
    def _generate_changes_html(self) -> str:
        """生成变化列表 HTML"""
        changes_html = []
        
        for i, change in enumerate(self.changes, 1):
            # 确定评分等级
            score_class = self._get_score_class(change.stability_score)
            confidence_class = self._get_score_class(change.confidence * 100)
            
            # 生成备选方案 HTML
            alternatives_html = ''
            if change.alternatives:
                alt_items = []
                for alt in change.alternatives[:3]:  # 最多显示3个
                    alt_items.append(f'''
                        <div class="alternative-item">
                            <span>{self._escape_html(alt)}</span>
                        </div>
                    ''')
                
                alternatives_html = f'''
                    <div class="alternatives">
                        <div class="alternatives-title">💡 备选方案</div>
                        <div class="alternatives-list">
                            {''.join(alt_items)}
                        </div>
                    </div>
                '''
            
            # 填充卡片模板
            card_html = self.CHANGE_CARD_TEMPLATE.format(
                number=i,
                stability_score=change.stability_score,
                confidence=change.confidence * 100,
                score_class=score_class,
                confidence_class=confidence_class,
                original_locator=self._escape_html(change.original_locator),
                optimized_locator=self._escape_html(change.optimized_locator),
                strategy_type=change.strategy_type,
                reason=self._escape_html(change.reason),
                alternatives_html=alternatives_html
            )
            
            changes_html.append(card_html)
        
        return '\n'.join(changes_html)
    
    def _get_score_class(self, score: float) -> str:
        """获取评分等级 CSS 类"""
        if score >= 90:
            return 'excellent'
        elif score >= 70:
            return 'good'
        else:
            return 'medium'
    
    def generate_text_report(self) -> str:
        """生成文本格式报告（终端输出）"""
        if not self.changes:
            return "✅ 所有定位器已经很稳定，无需优化"
        
        report_lines = [
            "\n" + "=" * 70,
            f"🔧 定位器优化报告 - 共优化 {len(self.changes)} 个定位器",
            "=" * 70
        ]
        
        for i, change in enumerate(self.changes, 1):
            report_lines.extend([
                f"\n{i}. 置信度: {change.confidence*100:.0f}% | 稳定性: {change.stability_score:.0f}分",
                f"   策略: {change.strategy_type}",
                f"   原始: {change.original_locator}",
                f"   优化: {change.optimized_locator}",
                f"   说明: {change.reason}"
            ])
            
            if change.alternatives:
                report_lines.append("   备选方案:")
                for j, alt in enumerate(change.alternatives[:2], 1):
                    report_lines.append(f"     {j}) {alt}")
        
        report_lines.append("\n" + "=" * 70)
        
        return '\n'.join(report_lines)
