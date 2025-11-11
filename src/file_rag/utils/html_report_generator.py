"""
HTML测试报告生成工具
负责将Markdown格式的测试报告转换为美观的HTML报告
"""
import os
import re
from datetime import datetime
from pathlib import Path


class HTMLReportGenerator:
    """HTML测试报告生成器"""
    
    @staticmethod
    def parse_markdown_report(markdown_content: str) -> dict:
        """
        解析Markdown格式的测试报告，提取关键信息
        
        Args:
            markdown_content: Markdown格式的测试报告内容
            
        Returns:
            包含报告各部分内容的字典
        """
        report_data = {
            "title": "自动化测试报告",
            "test_overview": "",
            "test_environment": "",
            "test_cases": [],
            "test_results": [],
            "statistics": {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "skipped": 0,
                "pass_rate": 0.0
            },
            "issues": "",
            "conclusion": "",
            "full_content": markdown_content
        }
        
        # 提取标题
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        if title_match:
            report_data["title"] = title_match.group(1)
        
        # 提取测试统计信息 - 改进版，支持多种格式
        # 方法1: 从表格中提取（优先）
        total_match = re.search(r'\|\s*总测试用例数\s*\|\s*(\d+)\s*\|', markdown_content)
        passed_match = re.search(r'\|\s*通过测试用例数\s*\|\s*(\d+)\s*\|', markdown_content)
        failed_match = re.search(r'\|\s*失败测试用例数\s*\|\s*(\d+)\s*\|', markdown_content)

        # 方法2: 从文本中提取
        if not total_match:
            total_match = re.search(r'总[测试用例]*数[：:]\s*(\d+)', markdown_content)
        if not passed_match:
            passed_match = re.search(r'通过[测试用例]*数[：:]\s*(\d+)', markdown_content)
        if not failed_match:
            failed_match = re.search(r'失败[测试用例]*数[：:]\s*(\d+)', markdown_content)

        # 方法3: 统计测试用例数量
        if not total_match:
            # 统计 TC-LOGIN-001 这样的用例编号
            tc_matches = re.findall(r'TC-[A-Z]+-\d+', markdown_content)
            if tc_matches:
                report_data["statistics"]["total"] = len(set(tc_matches))

        if total_match:
            report_data["statistics"]["total"] = int(total_match.group(1))
        if passed_match:
            report_data["statistics"]["passed"] = int(passed_match.group(1))
        if failed_match:
            report_data["statistics"]["failed"] = int(failed_match.group(1))

        # 如果没有找到通过数，尝试计算
        if report_data["statistics"]["passed"] == 0 and report_data["statistics"]["total"] > 0:
            # 统计通过的用例（包含 ✅ 或 "通过 ✅"）
            passed_cases = re.findall(r'(?:状态.*?通过.*?✅|✅.*?通过)', markdown_content)
            if passed_cases:
                report_data["statistics"]["passed"] = len(passed_cases)

        # 如果没有找到失败数，尝试计算
        if report_data["statistics"]["failed"] == 0 and report_data["statistics"]["total"] > 0:
            report_data["statistics"]["failed"] = (
                report_data["statistics"]["total"] -
                report_data["statistics"]["passed"]
            )

        # 计算通过率
        if report_data["statistics"]["total"] > 0:
            report_data["statistics"]["pass_rate"] = (
                report_data["statistics"]["passed"] /
                report_data["statistics"]["total"] * 100
            )
        
        # 提取测试用例信息 - 改进版，提取结构化数据
        test_cases = HTMLReportGenerator._extract_test_cases(markdown_content)
        report_data["test_cases"] = test_cases

        return report_data

    @staticmethod
    def _extract_test_cases(markdown_content: str) -> list:
        """
        从Markdown内容中提取测试用例的结构化数据（改进版，支持多种格式）

        Args:
            markdown_content: Markdown格式的测试报告内容

        Returns:
            测试用例列表，每个用例包含：编号、标题、目标、前置条件、步骤、预期结果、实际结果、状态
        """
        test_cases = []

        # 方法1: 从"测试执行详情"部分提取（新格式）
        # 匹配 "### 4.1 ✅ 测试用例 TC-LOGIN-001：成功登录测试" 这样的格式
        exec_pattern = r'###\s*\d+\.\d+\s*([✅❌⊘])\s*测试用例\s+(TC-[A-Z]+-\d+)[：:]\s*(.+?)(?=###\s*\d+\.\d+|##\s+\d+\.|$)'
        exec_matches = re.findall(exec_pattern, markdown_content, re.DOTALL)

        if exec_matches:
            # 使用新格式提取
            for status_icon, case_id, case_content in exec_matches:
                case_data = {
                    "number": case_id,
                    "title": "",
                    "objective": "",
                    "precondition": "",
                    "steps": "",
                    "expected": "",
                    "actual": "",
                    "status": "未知"
                }

                # 提取标题（第一行）
                title_match = re.search(r'^(.+?)(?:\n|$)', case_content.strip())
                if title_match:
                    case_data["title"] = title_match.group(1).strip()

                # 判断状态
                if status_icon == '✅':
                    case_data["status"] = "通过"
                elif status_icon == '❌':
                    case_data["status"] = "失败"
                elif status_icon == '⊘':
                    case_data["status"] = "跳过"

                # 提取执行步骤
                steps_match = re.search(r'\*\*执行步骤\*\*[：:]\s*(.+?)(?=\*\*验证结果\*\*|$)', case_content, re.DOTALL)
                if steps_match:
                    steps_text = steps_match.group(1).strip()
                    # 提取所有步骤（包含 ✅ 或 ❌ 的行）
                    step_lines = re.findall(r'[✅❌]\s*(.+)', steps_text)
                    if step_lines:
                        case_data["steps"] = '\n'.join([f"{i+1}. {step}" for i, step in enumerate(step_lines)])

                # 提取验证结果
                result_match = re.search(r'\*\*验证结果\*\*[：:]\s*(.+?)(?=\n\n|$)', case_content, re.DOTALL)
                if result_match:
                    case_data["actual"] = result_match.group(1).strip()

                test_cases.append(case_data)

            return test_cases

        # 方法2: 从"测试用例设计"表格中提取
        # 查找表格内容
        table_pattern = r'\|\s*用例编号\s*\|.+?\n\|[-:\s|]+\n((?:\|.+\|\n?)+)'
        table_match = re.search(table_pattern, markdown_content, re.DOTALL)

        if table_match:
            table_content = table_match.group(1)
            # 解析表格行
            table_rows = [line.strip() for line in table_content.split('\n') if line.strip() and line.strip().startswith('|')]

            for row in table_rows:
                cells = [cell.strip() for cell in row.split('|') if cell.strip()]
                if len(cells) >= 4:
                    case_data = {
                        "number": cells[0],
                        "title": cells[1],
                        "objective": cells[1],  # 使用测试场景作为目标
                        "precondition": "",
                        "steps": cells[2].replace('<br>', '\n'),  # 测试数据
                        "expected": cells[3],
                        "actual": "",
                        "status": "未知"
                    }
                    test_cases.append(case_data)

            # 如果从表格中提取到了用例，尝试从执行详情中补充状态
            if test_cases:
                for case in test_cases:
                    # 查找对应的执行详情
                    status_pattern = rf'{re.escape(case["number"])}[：:].+?状态.*?([通过失败跳过])\s*([✅❌⊘])'
                    status_match = re.search(status_pattern, markdown_content, re.DOTALL)
                    if status_match:
                        case["status"] = status_match.group(1)
                    else:
                        # 简单判断：如果包含 ✅，则通过
                        if f'{case["number"]}' in markdown_content:
                            if '✅' in markdown_content[markdown_content.find(case["number"]):markdown_content.find(case["number"])+500]:
                                case["status"] = "通过"

            return test_cases

        # 方法3: 旧格式 - 查找所有测试用例块
        # 匹配 "测试用例1：" 或 "### 测试用例1：" 格式
        case_pattern = r'(?:###\s*)?测试用例\s*(\d+)[：:]\s*(.+?)(?=(?:###\s*)?测试用例\s*\d+[：:]|##\s+\d+\.|$)'
        case_matches = re.findall(case_pattern, markdown_content, re.DOTALL)

        for case_num, case_content in case_matches:
            case_data = {
                "number": f"TC{case_num.zfill(3)}",
                "title": "",
                "objective": "",
                "precondition": "",
                "steps": "",
                "expected": "",
                "actual": "",
                "status": "未知"
            }

            # 提取标题（第一行）
            title_match = re.search(r'^(.+?)(?:\n|$)', case_content.strip())
            if title_match:
                case_data["title"] = title_match.group(1).strip()

            # 提取用例编号
            number_match = re.search(r'用例编号[：:]\s*(\w+)', case_content)
            if number_match:
                case_data["number"] = number_match.group(1)

            # 提取测试目标
            objective_match = re.search(r'测试目标[：:]\s*(.+?)(?=\n\s*[-*]|\n\n|$)', case_content, re.DOTALL)
            if objective_match:
                case_data["objective"] = objective_match.group(1).strip()

            # 提取前置条件
            precondition_match = re.search(r'前置条件[：:]\s*(.+?)(?=\n\s*[-*]|\n\n|$)', case_content, re.DOTALL)
            if precondition_match:
                case_data["precondition"] = precondition_match.group(1).strip()

            # 提取测试步骤
            steps_match = re.search(r'测试步骤[：:]\s*(.+?)(?=\n\s*[-*]\s*预期结果|\n\n|$)', case_content, re.DOTALL)
            if steps_match:
                steps_text = steps_match.group(1).strip()
                # 清理步骤文本
                steps_lines = [line.strip() for line in steps_text.split('\n') if line.strip()]
                case_data["steps"] = '\n'.join(steps_lines)

            # 提取预期结果
            expected_match = re.search(r'预期结果[：:]\s*(.+?)(?=\n\s*[-*]\s*实际结果|\n\n|$)', case_content, re.DOTALL)
            if expected_match:
                case_data["expected"] = expected_match.group(1).strip()

            # 提取实际结果和状态
            actual_match = re.search(r'实际结果[：:]\s*(.+?)(?=\n\n|$)', case_content, re.DOTALL)
            if actual_match:
                actual_text = actual_match.group(1).strip()
                case_data["actual"] = actual_text

                # 判断状态
                if '✅' in actual_text or '通过' in actual_text:
                    case_data["status"] = "通过"
                elif '❌' in actual_text or '失败' in actual_text:
                    case_data["status"] = "失败"
                elif '⊘' in actual_text or '跳过' in actual_text:
                    case_data["status"] = "跳过"

            test_cases.append(case_data)

        return test_cases

    @staticmethod
    def _generate_test_cases_table(test_cases: list) -> str:
        """
        生成测试用例表格的HTML

        Args:
            test_cases: 测试用例列表

        Returns:
            测试用例表格的HTML字符串
        """
        if not test_cases:
            return ""

        table_html = """
            <div class="test-cases-section">
                <h2>📋 测试用例详情</h2>
                <table class="test-cases-table">
                    <thead>
                        <tr>
                            <th>用例编号</th>
                            <th>用例标题</th>
                            <th>测试目标</th>
                            <th>前置条件</th>
                            <th>测试步骤</th>
                            <th>预期结果</th>
                            <th>实际结果</th>
                            <th>状态</th>
                        </tr>
                    </thead>
                    <tbody>
"""

        for case in test_cases:
            # 确定状态样式
            status_class = ""
            status_icon = ""
            if case['status'] == "通过":
                status_class = "status-passed"
                status_icon = "✓"
            elif case['status'] == "失败":
                status_class = "status-failed"
                status_icon = "✗"
            elif case['status'] == "跳过":
                status_class = "status-skipped"
                status_icon = "⊘"
            else:
                status_class = "status-skipped"
                status_icon = "?"

            # 处理实际结果文本（移除状态标记）
            actual_result = case['actual']
            actual_result = actual_result.replace('✅', '').replace('❌', '').replace('⊘', '')
            actual_result = actual_result.replace('通过 -', '').replace('失败 -', '').replace('跳过 -', '')
            actual_result = actual_result.strip()

            table_html += f"""
                        <tr>
                            <td class="case-number">{case['number']}</td>
                            <td class="case-title">{case['title']}</td>
                            <td>{case['objective']}</td>
                            <td>{case['precondition']}</td>
                            <td class="case-steps">{case['steps']}</td>
                            <td>{case['expected']}</td>
                            <td>{actual_result}</td>
                            <td class="case-status">
                                <span class="status-badge {status_class}">{status_icon} {case['status']}</span>
                            </td>
                        </tr>
"""

        table_html += """
                    </tbody>
                </table>
            </div>
"""

        return table_html

    @staticmethod
    def generate_html_report(markdown_content: str, output_path: str = None) -> str:
        """
        生成HTML格式的测试报告
        
        Args:
            markdown_content: Markdown格式的测试报告内容
            output_path: 输出文件路径（可选）
            
        Returns:
            生成的HTML文件路径
        """
        # 解析报告内容
        report_data = HTMLReportGenerator.parse_markdown_report(markdown_content)
        
        # 如果没有提供输出路径，自动生成
        if not output_path:
            # 创建 test_reports 目录
            reports_dir = Path("../src/test_reports")
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # 生成规范的文件名：测试报告_YYYYMMDD_HHMMSS.html
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"测试报告_{timestamp}.html"
            output_path = str(reports_dir / filename)
        else:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # 将Markdown转换为HTML（简单处理）
        html_content_body = HTMLReportGenerator._markdown_to_html(markdown_content)
        
        # 生成完整的HTML
        html_template = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Microsoft YaHei', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.15);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 36px;
            margin-bottom: 10px;
            font-weight: 600;
        }}
        
        .header .timestamp {{
            opacity: 0.95;
            font-size: 16px;
            margin-top: 10px;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
            border-bottom: 2px solid #e9ecef;
        }}
        
        .summary-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .summary-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        }}
        
        .summary-card .label {{
            font-size: 14px;
            color: #6c757d;
            margin-bottom: 10px;
            font-weight: 500;
        }}
        
        .summary-card .value {{
            font-size: 32px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        
        .summary-card.total .value {{ color: #495057; }}
        .summary-card.passed .value {{ color: #28a745; }}
        .summary-card.failed .value {{ color: #dc3545; }}
        .summary-card.rate .value {{ color: #007bff; }}
        
        .content {{
            padding: 40px;
        }}
        
        .content h1 {{
            color: #2c3e50;
            font-size: 28px;
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .content h2 {{
            color: #34495e;
            font-size: 24px;
            margin: 25px 0 15px 0;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        
        .content h3 {{
            color: #546e7a;
            font-size: 20px;
            margin: 20px 0 12px 0;
        }}
        
        .content p {{
            color: #555;
            margin: 12px 0;
            line-height: 1.8;
        }}
        
        .content ul, .content ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}
        
        .content li {{
            color: #555;
            margin: 8px 0;
            line-height: 1.7;
        }}
        
        .content table,
        .content-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            border-radius: 8px;
            overflow: hidden;
        }}

        .content table th,
        .content-table th {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}

        .content table td,
        .content-table td {{
            padding: 12px 15px;
            border-bottom: 1px solid #e9ecef;
        }}

        .content table tr:hover,
        .content-table tbody tr:hover {{
            background: #f8f9fa;
        }}

        .content-table tbody tr:nth-of-type(even) {{
            background-color: #f8f9fa;
        }}

        .content-table tbody tr:nth-of-type(even):hover {{
            background-color: #e3f2fd;
        }}
        
        .content code {{
            background: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Consolas', 'Monaco', monospace;
            color: #e83e8c;
        }}
        
        .content pre {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 8px;
            overflow-x: auto;
            margin: 20px 0;
        }}
        
        .content pre code {{
            background: none;
            color: inherit;
            padding: 0;
        }}
        
        .content blockquote {{
            border-left: 4px solid #667eea;
            padding-left: 20px;
            margin: 20px 0;
            color: #666;
            font-style: italic;
        }}
        
        .footer {{
            background: #f8f9fa;
            padding: 20px 30px;
            text-align: center;
            color: #6c757d;
            font-size: 14px;
            border-top: 2px solid #e9ecef;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
        }}

        .status-passed {{
            background: #d4edda;
            color: #155724;
        }}

        .status-failed {{
            background: #f8d7da;
            color: #721c24;
        }}

        .status-skipped {{
            background: #fff3cd;
            color: #856404;
        }}

        /* 测试用例表格专用样式 */
        .test-cases-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            font-size: 14px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }}

        .test-cases-table thead tr {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: left;
            font-weight: 600;
        }}

        .test-cases-table th {{
            padding: 14px 12px;
            font-size: 14px;
            white-space: nowrap;
        }}

        .test-cases-table tbody tr {{
            border-bottom: 1px solid #e9ecef;
            transition: background-color 0.2s;
        }}

        .test-cases-table tbody tr:nth-of-type(even) {{
            background-color: #f8f9fa;
        }}

        .test-cases-table tbody tr:hover {{
            background-color: #e3f2fd;
        }}

        .test-cases-table tbody tr:last-of-type {{
            border-bottom: 2px solid #667eea;
        }}

        .test-cases-table td {{
            padding: 12px;
            vertical-align: top;
        }}

        .test-cases-table td.case-number {{
            font-weight: 600;
            color: #667eea;
            text-align: center;
            width: 80px;
        }}

        .test-cases-table td.case-title {{
            font-weight: 600;
            color: #2c3e50;
            min-width: 150px;
        }}

        .test-cases-table td.case-steps {{
            font-size: 13px;
            line-height: 1.6;
            white-space: pre-wrap;
            max-width: 300px;
        }}

        .test-cases-table td.case-status {{
            text-align: center;
            width: 80px;
        }}

        .test-cases-section {{
            margin: 30px 0;
        }}

        .test-cases-section h2 {{
            color: #34495e;
            font-size: 24px;
            margin: 25px 0 20px 0;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }}
        
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            
            .container {{
                box-shadow: none;
            }}
            
            .summary-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 {report_data['title']}</h1>
            <div class="timestamp">
                📅 生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
            </div>
        </div>
        
        <div class="summary">
            <div class="summary-card total">
                <div class="label">总用例数</div>
                <div class="value">{report_data['statistics']['total']}</div>
            </div>
            <div class="summary-card passed">
                <div class="label">✓ 通过</div>
                <div class="value">{report_data['statistics']['passed']}</div>
            </div>
            <div class="summary-card failed">
                <div class="label">✗ 失败</div>
                <div class="value">{report_data['statistics']['failed']}</div>
            </div>
            <div class="summary-card rate">
                <div class="label">通过率</div>
                <div class="value">{report_data['statistics']['pass_rate']:.1f}%</div>
            </div>
        </div>
        
        <div class="content">
{html_content_body}

            <!-- 测试用例表格 -->
{HTMLReportGenerator._generate_test_cases_table(report_data['test_cases'])}
        </div>
        
        <div class="footer">
            <p>本报告由智能测试平台自动生成 | Powered by DeepSeek + MCP Chrome</p>
            <p>报告路径: {output_path}</p>
        </div>
    </div>
</body>
</html>
"""
        
        # 写入文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
        
        print(f"[HTML报告] ✓ 已生成HTML测试报告: {output_path}")
        
        return output_path
    
    @staticmethod
    def _markdown_to_html(markdown_text: str) -> str:
        """
        将Markdown文本转换为HTML（改进版，支持表格）

        Args:
            markdown_text: Markdown文本

        Returns:
            HTML文本
        """
        html = markdown_text

        # 转换Markdown表格为HTML表格
        html = HTMLReportGenerator._convert_markdown_tables(html)

        # 转换标题
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # 转换粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)

        # 转换代码块
        html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)

        # 转换行内代码
        html = re.sub(r'`(.+?)`', r'<code>\1</code>', html)

        # 转换列表
        html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        html = re.sub(r'^\d+\. (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)

        # 包装列表项
        html = re.sub(r'(<li>.+?</li>)', r'<ul>\1</ul>', html, flags=re.DOTALL)

        # 转换段落
        html = re.sub(r'\n\n', r'</p><p>', html)
        html = '<p>' + html + '</p>'

        # 清理多余的标签
        html = re.sub(r'<p>\s*<h', r'<h', html)
        html = re.sub(r'</h([123])>\s*</p>', r'</h\1>', html)
        html = re.sub(r'<p>\s*<ul>', r'<ul>', html)
        html = re.sub(r'</ul>\s*</p>', r'</ul>', html)
        html = re.sub(r'<p>\s*<table>', r'<table>', html)
        html = re.sub(r'</table>\s*</p>', r'</table>', html)
        html = re.sub(r'<p>\s*</p>', r'', html)

        return html

    @staticmethod
    def _convert_markdown_tables(markdown_text: str) -> str:
        """
        将Markdown表格转换为HTML表格

        Args:
            markdown_text: 包含Markdown表格的文本

        Returns:
            转换后的HTML文本
        """
        # 查找所有Markdown表格
        # 表格格式：
        # | 列1 | 列2 | 列3 |
        # |-----|-----|-----|
        # | 值1 | 值2 | 值3 |

        def replace_table(match):
            table_text = match.group(0)
            lines = [line.strip() for line in table_text.split('\n') if line.strip()]

            if len(lines) < 2:
                return table_text

            # 第一行是表头
            header_line = lines[0]
            headers = [cell.strip() for cell in header_line.split('|') if cell.strip()]

            # 第二行是分隔符（跳过）
            # 剩余行是数据
            data_lines = lines[2:] if len(lines) > 2 else []

            # 生成HTML表格
            html_table = '<table class="content-table">\n'

            # 表头
            html_table += '  <thead>\n    <tr>\n'
            for header in headers:
                html_table += f'      <th>{header}</th>\n'
            html_table += '    </tr>\n  </thead>\n'

            # 表体
            if data_lines:
                html_table += '  <tbody>\n'
                for data_line in data_lines:
                    cells = [cell.strip() for cell in data_line.split('|') if cell.strip()]
                    if cells:
                        html_table += '    <tr>\n'
                        for cell in cells:
                            # 处理单元格中的<br>标签
                            cell = cell.replace('<br>', '<br/>')
                            html_table += f'      <td>{cell}</td>\n'
                        html_table += '    </tr>\n'
                html_table += '  </tbody>\n'

            html_table += '</table>\n'

            return html_table

        # 匹配Markdown表格的正则表达式
        # 匹配至少2行的表格（表头 + 分隔符 + 可选的数据行）
        table_pattern = r'(?:^\|.+\|\s*$\n)+(?:^\|[-:\s|]+\|\s*$\n)(?:^\|.+\|\s*$\n)*'

        result = re.sub(table_pattern, replace_table, markdown_text, flags=re.MULTILINE)

        return result

