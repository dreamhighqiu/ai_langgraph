"""
工具模块 - 提供各种 MCP 工具的封装
添加了错误处理和延迟初始化机制

典型的mcp获取地址
https://mcp.so/server/playwright-mcp/microsoft
https://mcpservers.org/
https://modelscope.cn/mcp
"""

import asyncio
import os
from langchain_core.tools import tool
from typing import List, Dict, Any
from langchain_core.tools import BaseTool
from langchain_mcp_adapters.client import MultiServerMCPClient
# pip install openpyxl
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side


def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}，今天是晴天，温度为 25 摄氏度。"


def _safe_get_mcp_tools(client_config: dict, tool_name: str) -> List[BaseTool]:
    """
    安全地获取 MCP 工具，添加错误处理
    
    Args:
        client_config: MCP 客户端配置
        tool_name: 工具名称（用于日志）
    
    Returns:
        工具列表，如果失败则返回空列表
    """
    try:
        client = MultiServerMCPClient(client_config)
        tools = asyncio.run(client.get_tools())
        print(f"✓ 成功加载 {tool_name} 工具: {len(tools)} 个")
        return tools
    except Exception as e:
        print(f"✗ 加载 {tool_name} 工具失败: {str(e)}")
        return []


def get_tavily_search_mcp_tools() -> List[BaseTool]:
    """获取 Tavily 搜索 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "tavily_search": {
                "transport": "streamable_http",
                "url": "https://mcp.tavily.com/mcp/?tavilyApiKey=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"
            }
        },
        "Tavily Search"
    )


# def playwright_mcp_local_tools() -> List[BaseTool]:
#     """获取 Playwright MCP 本地工具"""
#     return _safe_get_mcp_tools(
#         {
#             "playwright_mcp": {
#                 "transport": "stdio",
#                 "command": "npx",
#                 "args": ["@playwright/mcp@latest"]
#             }
#         },
#         "Playwright"
#     )


def chrome_mcp_local_tools() -> List[BaseTool]:
    """获取 Chrome MCP 本地工具"""
    return _safe_get_mcp_tools(
        {
            "chrome_mcp": {
                "transport": "streamable_http",
                "url": "http://127.0.0.1:12306/mcp"
            }
        },
        "Chrome"
    )


def chart_mcp_tools() -> List[BaseTool]:
    """获取图表 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "chart_mcp": {
                "transport": "stdio",
                "command": "npx",
                "args": ["-y", "@antv/mcp-server-chart"]
            }
        },
        "Chart"
    )

def filesystem_mcp_tools() -> List[BaseTool]:
    """获取文件系统 MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "filesystem": {
                "args": [
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    "data/"
                    "."
                ],
                "command": "npx",
                "transport": "stdio"
            }
        },
        "Filesystem"
    )

def excel_mcp_tools() -> List[BaseTool]:
    """获取 Excel MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "excel_mcp": {
                "args": [
                    "--yes",
                    "@negokaz/excel-mcp-server"
                ],
                "command": "npx",
                "transport": "stdio",
                "env": {
                    "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
                }
            }
        },
        "Excel"
    )



def markdown_mcp_tools() -> List[BaseTool]:
    """获取 Markdown MCP 工具"""
    return _safe_get_mcp_tools(
        {
            "markdown_mcp": {
                "args": [
                    "/Users/qiuyunxia/code/ai_langGraph/markdownify-mcp/dist/index.js"
                ],
                "command": "node",
                "transport": "stdio",
                "env": {
                    "UV_PATH": "/opt/homebrew/bin/uv"
                }
            }
        },
        "Markdown"
    )

def time_mcp_tools() -> List[BaseTool]:
    """<UNK> Time MCP <UNK>"""
    return _safe_get_mcp_tools(
        {
            "time_mcp": {
                "args": [
                    "mcp-server-time"
                ],
                "command": "uvx",
                "transport": "stdio",
    }

        },
        "Time"
    )

def EdgeOne_mcp_tools() -> List[BaseTool]:
    return _safe_get_mcp_tools(

        {
            "edgeone_mcp": {
              "args": [
                "edgeone-pages-mcp"
              ],
            "command": "npx",
            "transport": "stdio",
    },

        },
        "EdgeOne"
    )


# ============================================================================
# 测试用例生成器专用工具组合
# ============================================================================

def get_test_case_generator_tools() -> List[BaseTool]:
    """
    获取测试用例生成器所需的 MCP 工具组合

    包含：
    - Excel MCP: 用于创建和编辑 Excel 文件
    - Filesystem MCP: 用于文件系统操作
    - Chart MCP: 用于绘制测试用例统计图表

    Returns:
        List[BaseTool]: 工具列表
    """
    tools = []

    # 添加 Excel 工具
    excel_tools = excel_mcp_tools()
    if excel_tools:
        tools.extend(excel_tools)
        print(f"✓ 已加载 Excel MCP 工具")

    # 添加文件系统工具
    fs_tools = filesystem_mcp_tools()
    if fs_tools:
        tools.extend(fs_tools)
        print(f"✓ 已加载 Filesystem MCP 工具")

    # 添加图表工具
    chart_tools = chart_mcp_tools()
    if chart_tools:
        tools.extend(chart_tools)
        print(f"✓ 已加载 Chart MCP 工具")

    return tools


@tool
def save_test_cases_to_excel(
    test_cases: List[Dict[str, Any]],
    file_path: str = "test_cases.xlsx",
    sheet_name: str = "测试用例",
    append: bool = False,
    columns: List[str] = None
) -> str:
    """
    将测试用例保存到Excel文件，支持专业格式化。

    此函数可以创建新的Excel文件或向现有文件追加测试用例数据，
    具有自动格式化、列宽调整和完善的错误处理功能。

    参数:
        test_cases: 测试用例列表，每个测试用例是一个字典。
                   示例结构:
                   [
                       {
                           "用例ID": "TC001",
                           "用例标题": "登录功能测试",
                           "前置条件": "用户已注册",
                           "测试步骤": "1. 打开登录页面\n2. 输入用户名和密码\n3. 点击登录按钮",
                           "预期结果": "成功登录并跳转到首页",
                           "优先级": "高",
                           "用例类型": "功能测试"
                       },
                       ...
                   ]
        file_path: Excel文件保存路径，默认为 "test_cases.xlsx"
        sheet_name: 工作表名称，默认为 "测试用例"
        append: 是否追加到现有文件，True表示追加，False表示创建新文件。默认为False
        columns: 可选的列名列表，用于指定列的顺序。
                如果为None，则自动从测试用例的键中检测列名。
                示例: ["用例ID", "用例标题", "优先级", "预期结果"]

    返回:
        str: 成功消息（包含文件路径和保存的测试用例数量）或错误消息

    异常:
        不会抛出异常，所有错误都会被捕获并作为错误消息返回

    使用示例:
        >>> test_data = [
        ...     {"用例ID": "TC001", "用例标题": "登录测试", "优先级": "高"},
        ...     {"用例ID": "TC002", "用例标题": "登出测试", "优先级": "中"}
        ... ]
        >>> result = save_test_cases_to_excel(test_data, "我的测试.xlsx")
        >>> print(result)
        成功创建！已保存 2 条测试用例到文件: /path/to/我的测试.xlsx
    """
    try:
        # 验证输入数据
        if not test_cases:
            return "错误：测试用例列表为空"

        if not isinstance(test_cases, list):
            return "错误：test_cases 必须是字典列表"

        # 确定要使用的列
        if columns is None:
            # 从所有测试用例中自动检测列名
            all_keys = []
            for case in test_cases:
                if not isinstance(case, dict):
                    return f"错误：每个测试用例必须是字典类型，当前发现 {type(case)}"
                for key in case.keys():
                    if key not in all_keys:
                        all_keys.append(key)
            columns = all_keys

        if not columns:
            return "错误：在测试用例中未找到任何列"

        # 定义Excel样式
        # 表头样式：白色粗体文字，蓝色背景
        header_font = Font(name='Arial', size=11, bold=True, color='FFFFFF')
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)

        # 单元格样式：普通字体，左对齐，自动换行
        cell_font = Font(name='Arial', size=10)
        cell_alignment = Alignment(horizontal='left', vertical='top', wrap_text=True)

        # 边框样式：细黑色边框
        thin_border = Border(
            left=Side(style='thin', color='000000'),
            right=Side(style='thin', color='000000'),
            top=Side(style='thin', color='000000'),
            bottom=Side(style='thin', color='000000')
        )

        # 判断是追加模式还是创建新文件
        if append and os.path.exists(file_path):
            # 追加模式：加载现有文件
            try:
                wb = load_workbook(file_path)
                if sheet_name in wb.sheetnames:
                    # 工作表已存在，追加到末尾
                    ws = wb[sheet_name]
                    start_row = ws.max_row + 1
                else:
                    # 工作表不存在，创建新工作表
                    ws = wb.create_sheet(sheet_name)
                    start_row = 1
            except Exception as e:
                return f"错误：加载现有文件失败: {str(e)}"
        else:
            # 创建新文件
            wb = Workbook()
            ws = wb.active
            ws.title = sheet_name
            start_row = 1

        # 如果是新工作表，写入表头行
        if start_row == 1:
            for col_idx, header in enumerate(columns, start=1):
                cell = ws.cell(row=1, column=col_idx, value=header)
                cell.font = header_font
                cell.fill = header_fill
                cell.alignment = header_alignment
                cell.border = thin_border
            start_row = 2  # 数据从第2行开始

        # 写入测试用例数据
        for row_idx, test_case in enumerate(test_cases, start=start_row):
            for col_idx, column_name in enumerate(columns, start=1):
                # 获取字典中的值，如果不存在则为空字符串
                value = test_case.get(column_name, "")
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                cell.font = cell_font
                cell.alignment = cell_alignment
                cell.border = thin_border

        # 根据内容类型自动调整列宽
        for col_idx, column_name in enumerate(columns, start=1):
            column_letter = ws.cell(row=1, column=col_idx).column_letter

            # 根据列名模式设置默认宽度
            # ID、优先级、类型、状态等短字段：15个字符宽度
            if any(keyword in column_name.lower() for keyword in ['id', 'priority', 'type', 'status', '优先级', '类型', '状态']):
                ws.column_dimensions[column_letter].width = 15
            # 标题、名称、摘要等中等字段：30个字符宽度
            elif any(keyword in column_name.lower() for keyword in ['title', 'name', 'summary', '标题', '名称', '摘要']):
                ws.column_dimensions[column_letter].width = 30
            # 步骤、结果、描述、详情等长字段：50个字符宽度
            elif any(keyword in column_name.lower() for keyword in ['step', 'result', 'description', 'detail', '步骤', '结果', '描述', '详情', '条件']):
                ws.column_dimensions[column_letter].width = 50
            # 其他字段：25个字符宽度
            else:
                ws.column_dimensions[column_letter].width = 25

        # 设置行高以提高可读性
        for row in ws.iter_rows(min_row=1, max_row=ws.max_row):
            ws.row_dimensions[row[0].row].height = 30

        # 保存文件
        try:
            wb.save(file_path)
        except PermissionError:
            return f"错误：权限被拒绝。文件 '{file_path}' 可能正在其他程序中打开。"
        except Exception as e:
            return f"错误：保存文件失败: {str(e)}"

        # 生成成功消息
        mode_text = "追加" if (append and os.path.exists(file_path)) else "创建"
        abs_path = os.path.abspath(file_path)
        return f"成功{mode_text}！已保存 {len(test_cases)} 条测试用例到文件: {abs_path}"

    except Exception as e:
        return f"未预期的错误: {str(e)}"


# 测试代码（取消注释以测试）
if __name__ == "__main__":
    print("测试工具加载...")
    print("\n1. 测试 Tavily Search:")
    get_tavily_search_mcp_tools()

    print("\n2. 测试 Chart:")
    chart_mcp_tools()

    print("\n3. 测试 Filesystem:")
    filesystem_mcp_tools()

    print("\n4. 测试 Excel:")
    excel_mcp_tools()

    print("\n5. 测试用例生成器工具组合:")
    get_test_case_generator_tools()