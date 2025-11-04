"""
通用测试用例生成器 - 支持所有功能的测试用例生成（集成 MCP 工具）

功能：
1. 根据功能需求生成测试用例（节点1）- 不依赖数据库
2. 评审测试用例质量（节点2，最多3次）
3. 使用 Filesystem MCP 工具保存 Excel 和 JSON 文件到 data 目录（节点4）
4. 使用图表 MCP 工具生成统计图表（节点5）

工作流程：
START -> 节点1(生成) -> 节点2(评审) -> 条件判断 -> 节点3(准备) -> 节点4(Filesystem MCP)
                                           ↓                              ↓
                                      返回节点1(重新生成)          节点5(图表 MCP) -> END

MCP 工具集成：
- Filesystem MCP: 用于文件系统操作，保存 Excel 和 JSON 格式的测试用例到 data/ 目录
- Chart MCP: 用于生成测试用例分类统计图表（柱状图、饼图等）

提示词策略：
- 使用 Filesystem MCP 工具处理所有文件操作（包括 Excel 和 JSON）
- 通过 LLM Agent 来协调 MCP 工具的调用
- 使用清晰的提示词限制和要求，确保工具正确使用
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph
from langchain.agents import create_agent
from llm import create_llm
from tools import (
    filesystem_mcp_tools,
    chart_mcp_tools
)

# 创建 LLM 实例
llm = create_llm()

# 初始化 MCP 工具
_filesystem_tools = filesystem_mcp_tools()
_chart_tools = chart_mcp_tools()
_all_mcp_tools =  _filesystem_tools + _chart_tools


# ============================================================================
# 自定义状态类 - 扩展 MessagesState
# ============================================================================

class TestCaseState(MessagesState):
    """测试用例生成状态"""
    requirement: str = ""  # 需求描述
    review_count: int = 0  # 评审次数
    test_cases: str = ""  # 生成的测试用例（JSON 格式）
    review_passed: bool = False  # 评审是否通过
    review_feedback: str = ""  # 评审反馈
    excel_file_path: str = ""  # 保存的 Excel 文件路径
    json_file_path: str = ""  # 保存的 JSON 文件路径
    chart_data: str = ""  # 图表数据（JSON 格式）
    chart_generated: bool = False  # 图表是否已生成


# ============================================================================
# 节点函数定义
# ============================================================================

def generate_test_cases_node(state: TestCaseState) -> dict:
    """
    节点1：生成测试用例
    根据功能需求生成测试用例，不依赖数据库
    """
    # 安全地获取状态字段，使用默认值
    review_count = state.get('review_count', 0)

    # 判断是否是重新生成（从评审节点返回）
    is_regenerate = review_count > 0

    print("\n" + "=" * 80)
    if is_regenerate:
        print(f"📝 节点1：重新生成测试用例 (第 {review_count} 次评审后重新生成)")
    else:
        print(f"📝 节点1：生成测试用例 (第 1 次生成)")
    print("=" * 80)

    # 构建提示词
    if not is_regenerate:
        # 第一次生成
        system_prompt = """你是一个专业的测试工程师，负责生成高质量的功能测试用例。

请根据以下要求生成测试用例：
1. 支持所有功能的测试用例（不限于数据库操作）
2. 包含：正常场景、边界场景、异常场景、性能场景等
3. 每个测试用例包含：用例ID、用例名称、前置条件、测试步骤、预期结果、优先级
4. 生成 8-15 条测试用例
5. 以 JSON 格式返回，格式如下：
{
    "test_cases": [
        {
            "case_id": "TC001",
            "case_name": "用例名称",
            "priority": "P0",
            "precondition": "前置条件",
            "test_steps": "1. 步骤1\\n2. 步骤2\\n3. 步骤3",
            "expected_result": "预期结果",
            "category": "正常场景"
        }
    ]
}"""
        requirement = state.get('requirement', '通用功能测试')
        user_message = f"请为以下功能生成测试用例：\n{requirement}"
    else:
        # 根据评审反馈重新生成
        system_prompt = """你是一个专业的测试工程师，负责生成高质量的功能测试用例。

之前生成的测试用例未通过评审，请根据评审反馈改进测试用例。

要求：
1. 仔细阅读评审反馈
2. 针对性地改进测试用例
3. 确保测试用例的完整性、清晰性和可执行性
4. 以 JSON 格式返回"""
        review_feedback = state.get('review_feedback', '')
        user_message = f"评审反馈：\n{review_feedback}\n\n请根据反馈改进测试用例。"

    # 调用 LLM 生成测试用例
    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    test_cases_content = response.content

    print(f"\n生成的测试用例：\n{test_cases_content[:500]}...")

    return {
        "messages": [response],
        "test_cases": test_cases_content,
        "review_count": 0  # 重置评审计数为 0，因为这是新一轮的生成
    }


def review_test_cases_node(state: TestCaseState) -> dict:
    """
    节点2：评审测试用例
    使用 LLM 评审测试用例的质量
    """
    # 安全地获取状态字段
    review_count = state.get('review_count', 0)

    print("\n" + "=" * 80)
    print(f"🔍 节点2：评审测试用例 (第 {review_count + 1} 次评审)")
    print("=" * 80)

    # 构建评审提示词
    system_prompt = """你是一个资深的测试评审专家，负责评审测试用例的质量。

评审标准：
1. 测试用例是否完整（包含用例ID、名称、前置条件、步骤、预期结果、优先级）
2. 测试步骤是否清晰、可执行、具体
3. 预期结果是否明确、可验证
4. 是否覆盖了正常场景、边界场景、异常场景
5. 优先级划分是否合理
6. JSON 格式是否正确

请给出评审结果：
- 如果通过，返回 JSON: {"passed": true, "feedback": "评审通过，测试用例质量良好"}
- 如果不通过，返回 JSON: {"passed": false, "feedback": "具体的改进建议"}"""

    test_cases = state.get('test_cases', '')
    user_message = f"请评审以下测试用例：\n\n{test_cases}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_message)
    ]

    response = llm.invoke(messages)
    review_result = response.content

    print(f"\n评审结果：\n{review_result}")

    # 解析评审结果
    try:
        # 尝试从响应中提取 JSON
        json_match = re.search(r'\{.*\}', review_result, re.DOTALL)
        if json_match:
            review_data = json.loads(json_match.group())
            passed = review_data.get('passed', False)
            feedback = review_data.get('feedback', '')
        else:
            # 如果没有找到 JSON，根据关键词判断
            passed = '通过' in review_result or 'passed' in review_result.lower()
            feedback = review_result
    except Exception:
        # 解析失败，默认不通过
        passed = False
        feedback = review_result

    return {
        "messages": [response],
        "review_count": review_count + 1,
        "review_passed": passed,
        "review_feedback": feedback
    }


def save_to_excel_node(state: TestCaseState) -> dict:
    """
    节点3：保存测试用例到 Excel（使用 MCP 工具）

    使用 Excel MCP 工具创建 Excel 文件并通过 Filesystem MCP 保存到 data/ 目录
    """
    print("\n" + "=" * 80)
    print("💾 节点3：保存测试用例到 Excel（使用 MCP 工具）")
    print("=" * 80)

    try:
        # 安全地获取状态字段
        test_cases = state.get('test_cases', '')
        review_count = state.get('review_count', 0)
        review_passed = state.get('review_passed', False)

        # 生成文件名和路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_cases_{timestamp}.xlsx"
        file_path = f"data/{filename}"

        # 解析测试用例 JSON
        test_cases_list = []
        print(f"\n🔍 开始解析测试用例数据...")
        print(f"   原始数据长度: {len(test_cases)} 字符")

        try:
            # 尝试直接解析
            test_cases_data = json.loads(test_cases)
            if isinstance(test_cases_data, dict) and 'test_cases' in test_cases_data:
                test_cases_list = test_cases_data['test_cases']
            elif isinstance(test_cases_data, list):
                test_cases_list = test_cases_data
            else:
                test_cases_list = [test_cases_data]
            print(f"   ✅ 直接解析成功，获得 {len(test_cases_list)} 条用例")
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试从文本中提取 JSON
            print(f"   ⚠️ 直接解析失败: {str(e)[:100]}")
            print(f"   🔄 尝试从文本中提取 JSON...")
            try:
                # 查找 JSON 块（从 { 或 [ 开始）
                import re
                json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', test_cases)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"   📍 找到 JSON 块，长度: {len(json_str)} 字符")
                    test_cases_data = json.loads(json_str)
                    if isinstance(test_cases_data, dict) and 'test_cases' in test_cases_data:
                        test_cases_list = test_cases_data['test_cases']
                    elif isinstance(test_cases_data, list):
                        test_cases_list = test_cases_data
                    else:
                        test_cases_list = [test_cases_data]
                    print(f"   ✅ 提取解析成功，获得 {len(test_cases_list)} 条用例")
                else:
                    print(f"   ❌ 未找到 JSON 块")
            except (json.JSONDecodeError, AttributeError) as e:
                test_cases_list = []
                print(f"   ❌ 提取解析失败: {str(e)[:100]}")
                print(f"   原始数据: {test_cases[:300]}...")

        # 生成统计数据用于图表
        chart_data = {
            "total_cases": len(test_cases_list),
            "review_count": review_count,
            "passed": review_passed,
            "timestamp": timestamp,
            "categories": _count_test_case_categories(test_cases_list)
        }

        # 构建结果消息
        result_msg = f"✅ 测试用例已准备好保存\n"
        result_msg += f"文件名: {filename}\n"
        result_msg += f"保存路径: {file_path}\n"
        result_msg += f"测试用例数量: {len(test_cases_list)}\n"
        result_msg += f"评审次数: {review_count}\n"
        result_msg += f"评审状态: {'通过' if review_passed else '未通过'}\n"
        result_msg += f"\n可通过 MCP 工具进行以下操作：\n"
        result_msg += f"1. 使用 Excel MCP 工具创建和编辑 Excel 文件\n"
        result_msg += f"2. 使用 Filesystem MCP 工具保存到 data/ 目录\n"
        result_msg += f"3. 使用 Chart MCP 工具生成统计图表"

        print(f"\n{result_msg}")

        return {
            "messages": [AIMessage(content=result_msg)],
            "excel_file_path": file_path,
            "chart_data": json.dumps(chart_data)
        }

    except Exception as e:
        error_msg = f"❌ 保存失败: {str(e)}"
        print(f"\n{error_msg}")
        return {
            "messages": [AIMessage(content=error_msg)]
        }


def _count_test_case_categories(test_cases_list: list) -> dict:
    """
    统计测试用例的分类信息
    """
    categories = {}
    for case in test_cases_list:
        category = case.get('category', '其他')
        categories[category] = categories.get(category, 0) + 1
    return categories


def save_to_filesystem_node(state: TestCaseState) -> dict:
    """
    节点4：使用 Filesystem MCP 工具保存 Excel 和 JSON 文件到 data 目录

    通过 LLM 调用 Filesystem MCP 工具保存测试用例数据为 Excel 和 JSON 格式
    """
    print("\n" + "=" * 80)
    print("💾 节点4：使用 Filesystem MCP 工具保存文件到 data 目录")
    print("=" * 80)

    try:
        # 获取状态数据
        test_cases = state.get('test_cases', '')

        # 生成文件路径
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"test_cases_{timestamp}.xlsx"
        json_filename = f"test_cases_{timestamp}.json"
        excel_file_path = f"data/{excel_filename}"
        json_file_path = f"data/{json_filename}"

        # 解析测试用例数据
        test_cases_list = []
        print(f"\n🔍 开始解析测试用例数据...")
        print(f"   原始数据长度: {len(test_cases)} 字符")

        try:
            # 尝试直接解析
            test_cases_data = json.loads(test_cases)
            if isinstance(test_cases_data, dict) and 'test_cases' in test_cases_data:
                test_cases_list = test_cases_data['test_cases']
            elif isinstance(test_cases_data, list):
                test_cases_list = test_cases_data
            else:
                test_cases_list = [test_cases_data]
            print(f"   ✅ 直接解析成功，获得 {len(test_cases_list)} 条用例")
        except json.JSONDecodeError as e:
            # 如果直接解析失败，尝试从文本中提取 JSON
            print(f"   ⚠️ 直接解析失败: {str(e)[:100]}")
            print(f"   🔄 尝试从文本中提取 JSON...")
            try:
                json_match = re.search(r'(\{[\s\S]*\}|\[[\s\S]*\])', test_cases)
                if json_match:
                    json_str = json_match.group(1)
                    print(f"   📍 找到 JSON 块，长度: {len(json_str)} 字符")
                    test_cases_data = json.loads(json_str)
                    if isinstance(test_cases_data, dict) and 'test_cases' in test_cases_data:
                        test_cases_list = test_cases_data['test_cases']
                    elif isinstance(test_cases_data, list):
                        test_cases_list = test_cases_data
                    else:
                        test_cases_list = [test_cases_data]
                    print(f"   ✅ 提取解析成功，获得 {len(test_cases_list)} 条用例")
                else:
                    print(f"   ❌ 未找到 JSON 块")
            except (json.JSONDecodeError, AttributeError) as e:
                test_cases_list = []
                print(f"   ❌ 提取解析失败: {str(e)[:100]}")

        # 构建结构化的 Excel 数据
        excel_data_for_mcp = []
        for case in test_cases_list:
            excel_data_for_mcp.append({
                "用例ID": case.get('case_id', ''),
                "用例名称": case.get('case_name', ''),
                "优先级": case.get('priority', ''),
                "前置条件": case.get('precondition', ''),
                "测试步骤": case.get('test_steps', ''),
                "预期结果": case.get('expected_result', ''),
                "分类": case.get('category', '')
            })

        # 数据验证
        print(f"\n📊 数据验证:")
        print(f"   - 测试用例总数: {len(test_cases_list)}")
        print(f"   - Excel 数据行数: {len(excel_data_for_mcp)}")
        if excel_data_for_mcp:
            print(f"   - 第一条数据: {excel_data_for_mcp[0]}")
        else:
            print("   ⚠️ 警告：没有测试用例数据，Excel 将为空")

        # 构建文件系统操作提示词 - 分别处理 Excel 和 JSON
        excel_prompt = f"""请使用 Filesystem MCP 工具创建一个 Excel 文件。

文件路径: {excel_file_path}

数据信息:
- 总数据行数: {len(test_cases_list)}
- 表头: 用例ID | 用例名称 | 优先级 | 前置条件 | 测试步骤 | 预期结果 | 分类

数据内容（JSON 格式）:
{json.dumps(excel_data_for_mcp, ensure_ascii=False, indent=2)}

要求:
1. 创建一个 .xlsx 格式的 Excel 文件
2. 第一行为表头，包含以下列（按顺序）：用例ID、用例名称、优先级、前置条件、测试步骤、预期结果、分类
3. 从第二行开始，按照上述 JSON 数据填充每一行（共 {len(test_cases_list)} 行数据）
4. 确保每一行都有数据，不要遗漏任何数据行
5. 格式要求：
   - 使用 UTF-8 编码
   - 表头行加粗、背景色为蓝色、文字颜色为白色
   - 设置列宽：用例ID(12)、用例名称(20)、优先级(10)、前置条件(20)、测试步骤(30)、预期结果(30)、分类(15)
   - 数据行启用自动换行
   - 所有中文字符必须正确显示
6. 使用 Filesystem MCP 工具完成所有操作"""

        json_prompt = f"""请使用 Filesystem MCP 工具创建一个 JSON 文件。

文件路径: {json_file_path}

要求:
1. 创建一个 .json 格式的文件
2. 保存以下测试用例数据：

{json.dumps(test_cases_data if 'test_cases_data' in locals() else test_cases_list, ensure_ascii=False, indent=2)}

3. 格式要求：
   - 使用 UTF-8 编码
   - 格式化输出（缩进 2 个空格）
   - 所有中文字符必须正确显示

4. 使用 Filesystem MCP 工具完成所有操作"""

        # 创建 Agent 来调用 MCP 工具
        fs_agent = create_agent(
            model=llm,
            tools=_filesystem_tools,
            system_prompt="你是一个专业的文件系统操作助手。你必须使用 Filesystem MCP 工具创建 Excel 和 JSON 文件。确保所有中文字符正确显示，使用 UTF-8 编码。"
        )

        # 先创建 Excel 文件
        print("\n📝 正在创建 Excel 文件...")
        try:
            result_excel = asyncio.run(fs_agent.ainvoke({
                "messages": [{"role": "user", "content": excel_prompt}]
            }))
            excel_result_msg = result_excel["messages"][-1].content if result_excel["messages"] else "Excel 文件创建完成"
            print(f"✅ Excel 文件已创建: {excel_file_path}")
            print(f"   结果: {excel_result_msg[:150]}...")
        except Exception as e:
            print(f"❌ Excel 文件创建失败: {str(e)}")
            excel_result_msg = f"Excel 创建失败: {str(e)}"

        # 再创建 JSON 文件
        print("\n📝 正在创建 JSON 文件...")
        try:
            result_json = asyncio.run(fs_agent.ainvoke({
                "messages": [{"role": "user", "content": json_prompt}]
            }))
            json_result_msg = result_json["messages"][-1].content if result_json["messages"] else "JSON 文件创建完成"
            print(f"✅ JSON 文件已创建: {json_file_path}")
            print(f"   结果: {json_result_msg[:150]}...")
        except Exception as e:
            print(f"❌ JSON 文件创建失败: {str(e)}")
            json_result_msg = f"JSON 创建失败: {str(e)}"

        result_msg = f"Excel: {excel_result_msg}\n\nJSON: {json_result_msg}"

        # 构建图表数据
        review_count = state.get('review_count', 0)
        review_passed = state.get('review_passed', False)

        chart_data = {
            "total_cases": len(test_cases_list),
            "review_count": review_count,
            "passed": review_passed,
            "timestamp": timestamp,
            "categories": _count_test_case_categories(test_cases_list)
        }

        print(f"\n📊 图表数据已构建:")
        print(f"   - 总用例数: {chart_data['total_cases']}")
        print(f"   - 评审次数: {chart_data['review_count']}")
        print(f"   - 评审状态: {'通过' if chart_data['passed'] else '未通过'}")
        print(f"   - 分类统计: {chart_data['categories']}")

        return {
            "messages": [AIMessage(content=f"✅ 文件已保存到 data 目录\n{result_msg}")],
            "excel_file_path": excel_file_path,
            "json_file_path": json_file_path,
            "chart_data": json.dumps(chart_data, ensure_ascii=False)
        }

    except Exception as e:
        error_msg = f"❌ 文件保存失败: {str(e)}"
        print(f"\n{error_msg}")
        return {
            "messages": [AIMessage(content=error_msg)]
        }


def generate_chart_node(state: TestCaseState) -> dict:
    """
    节点5：使用图表 MCP 工具生成测试用例统计图表

    通过 LLM 调用图表 MCP 工具生成统计图表
    """
    print("\n" + "=" * 80)
    print("📈 节点5：使用图表 MCP 工具生成统计图表")
    print("=" * 80)

    try:
        # 获取状态数据
        chart_data = state.get('chart_data', '')

        # 解析图表数据
        try:
            chart_info = json.loads(chart_data)
        except json.JSONDecodeError:
            chart_info = {}

        # 构建图表生成提示词
        chart_prompt = f"""请使用图表 MCP 工具生成测试用例统计图表。

统计数据:
- 总测试用例数: {chart_info.get('total_cases', 0)}
- 评审次数: {chart_info.get('review_count', 0)}
- 评审状态: {'通过' if chart_info.get('passed', False) else '未通过'}
- 用例分类统计: {json.dumps(chart_info.get('categories', {}), ensure_ascii=False)}

要求:
1. 使用图表 MCP 工具创建以下图表:
   - 柱状图: 显示各分类的测试用例数量
   - 饼图: 显示测试用例的分类占比
2. 图表标题应该清晰明了
3. 包含图表说明和数据标签
4. 不要自己编写图表代码，使用图表 MCP 工具完成所有操作"""

        # 创建 Agent 来调用 MCP 工具
        chart_agent = create_agent(
            model=llm,
            tools=_chart_tools,
            system_prompt="你是一个专业的数据可视化助手，使用图表 MCP 工具生成各种统计图表。"
        )

        # 调用 Agent（使用异步调用）
        result = asyncio.run(chart_agent.ainvoke({
            "messages": [{"role": "user", "content": chart_prompt}]
        }))

        # 提取结果
        result_msg = result["messages"][-1].content if result["messages"] else "图表生成完成"

        print(f"\n✅ 统计图表已生成")
        print(f"结果: {result_msg[:200]}...")

        return {
            "messages": [AIMessage(content=f"✅ 统计图表已生成\n{result_msg}")],
            "chart_generated": True
        }

    except Exception as e:
        error_msg = f"❌ 图表生成失败: {str(e)}"
        print(f"\n{error_msg}")
        return {
            "messages": [AIMessage(content=error_msg)]
        }


# ============================================================================
# 条件边函数
# ============================================================================

def condition_edge(state: TestCaseState) -> Literal["generate_node", "save_node"]:
    """
    条件边（节点4）：判断流程走向

    逻辑：
    - 如果评审通过，进入节点3（保存）
    - 如果评审次数 >= 3（达到最大次数），进入节点3（保存）
    - 否则，返回节点1（重新生成）
    """
    # 安全地获取状态字段
    review_count = state.get('review_count', 0)
    review_passed = state.get('review_passed', False)

    print("\n" + "=" * 80)
    print(f"🔀 条件判断：评审次数={review_count}, 是否通过={review_passed}")
    print("=" * 80)

    if review_passed:
        print("✅ 决策：评审通过 → 进入节点3（保存到Excel）")
        return "save_node"
    elif review_count >= 3:
        print("⚠️ 决策：已达到最大评审次数（3次） → 进入节点3（保存到Excel）")
        return "save_node"
    else:
        print(f"🔄 决策：评审不通过，返回节点1（重新生成测试用例，已评审 {review_count} 次）")
        return "generate_node"


# ============================================================================
# 构建工作流
# ============================================================================

def create_test_case_workflow():
    """创建测试用例生成工作流"""

    # 创建状态图
    workflow = StateGraph(TestCaseState)

    # 添加节点
    workflow.add_node("generate_node", generate_test_cases_node)          # 节点1：生成测试用例
    workflow.add_node("review_node", review_test_cases_node)              # 节点2：评审测试用例
    workflow.add_node("save_node", save_to_excel_node)                    # 节点3：准备保存
    workflow.add_node("filesystem_node", save_to_filesystem_node)         # 节点4：Filesystem MCP 保存
    workflow.add_node("chart_node", generate_chart_node)                  # 节点5：图表 MCP 生成

    # 添加边
    workflow.add_edge(START, "generate_node")                             # 开始 -> 节点1
    workflow.add_edge("generate_node", "review_node")                     # 节点1 -> 节点2
    workflow.add_conditional_edges(
        "review_node",                                                    # 节点2 -> 条件边
        condition_edge,                                                   # 条件函数
        {
            "generate_node": "generate_node",                             # 不通过 -> 节点1
            "save_node": "save_node"                                      # 通过 -> 节点3
        }
    )
    workflow.add_edge("save_node", "filesystem_node")                     # 节点3 -> 节点4（Filesystem MCP）
    workflow.add_edge("filesystem_node", "chart_node")                    # 节点4 -> 节点5（图表 MCP）
    workflow.add_edge("chart_node", END)                                  # 节点5 -> 结束

    # 编译工作流
    return workflow.compile()


# ============================================================================
# 创建 Graph（用于 LangGraph 启动）
# ============================================================================

# 创建工作流图，用于 graph.json 中的注册
graph = create_test_case_workflow()


# ============================================================================
# 主函数和工作流执行
# ============================================================================

async def query_test_case_generator(requirement: str):
    """
    查询测试用例生成器并返回结果

    参数:
        requirement: 功能需求描述
    """
    print("\n" + "=" * 80)
    print(f"需求: {requirement}")
    print("=" * 80 + "\n")

    # 初始化状态
    initial_state = {
        "messages": [],
        "requirement": requirement,
        "review_count": 0,
        "test_cases": "",
        "review_passed": False,
        "review_feedback": "",
        "excel_file_path": "",
        "json_file_path": "",
        "chart_data": "",
        "chart_generated": False
    }

    # 执行工作流
    final_state = graph.invoke(initial_state)

    # 打印最终结果
    print("\n" + "=" * 80)
    print("🎉 工作流执行完成")
    print("=" * 80)
    print(f"总评审次数: {final_state['review_count']}")
    print(f"评审结果: {'通过' if final_state['review_passed'] else '未通过（达到最大次数）'}")
    if final_state.get('excel_file_path'):
        print(f"✅ Excel 文件: {final_state['excel_file_path']}")
    if final_state.get('json_file_path'):
        print(f"✅ JSON 文件: {final_state['json_file_path']}")
    if final_state.get('chart_generated'):
        print(f"✅ 统计图表已生成")
    print("=" * 80)

    return final_state


async def main():
    """主函数 - 演示如何使用测试用例生成器"""

    # 打印配置信息
    print("=" * 60)
    print("通用测试用例生成器（集成 MCP 工具）")
    print("=" * 60)
    print("功能：")
    print("1. 根据功能需求生成测试用例")
    print("2. 自动评审测试用例质量（最多3次）")
    print("3. 使用 Filesystem MCP 工具保存 Excel 和 JSON 文件到 data 目录")
    print("4. 使用图表 MCP 工具生成统计图表")
    print("=" * 60)

    # 示例需求列表
    requirements = [
        "请为用户管理系统生成测试用例，包括用户注册、登录、信息修改、删除等功能",
        # 你可以根据实际需求添加更多需求
    ]

    # 执行查询
    for requirement in requirements:
        await query_test_case_generator(requirement)
        print("\n" + "-" * 60 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

