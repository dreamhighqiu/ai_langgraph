"""
测试用例生成系统 - 基于 LangGraph 实现
包含三个节点：编写测试用例、评审测试用例、保存到Excel
参照 tool_call_example_condition.py 的模式优化
"""

import json
import os
from typing import TypedDict, Annotated, List, Dict, Any
from datetime import datetime

from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

from llm import create_llm
from tools import save_test_cases_to_excel


# ============================================================================
# 常量定义
# ============================================================================

# 测试用例必需字段
REQUIRED_FIELDS = [
    "用例ID",
    "用例标题",
    "前置条件",
    "测试步骤",
    "预期结果",
    "优先级",
    "用例类型"
]

# 优先级枚举
PRIORITY_LEVELS = ["高", "中", "低"]

# 用例类型枚举
TEST_CASE_TYPES = ["功能测试", "性能测试", "安全测试", "兼容性测试", "集成测试", "回归测试"]

# 最大评审次数
MAX_REVIEW_COUNT = 3


# ============================================================================
# 状态定义
# ============================================================================

class TestCaseState(TypedDict):
    """测试用例生成系统的状态"""
    messages: Annotated[list[AnyMessage], add_messages]
    test_cases: List[Dict[str, Any]]  # 生成的测试用例
    review_count: int  # 评审次数
    review_passed: bool  # 是否通过评审
    file_path: str  # 保存的文件路径
    review_feedback: str  # 评审反馈信息


# ============================================================================
# 节点定义
# ============================================================================

def write_test_case_node(state: TestCaseState) -> TestCaseState:
    """
    节点1：编写测试用例
    直接与大模型交互，生成高质量的测试用例

    流程：
    1. 获取用户需求
    2. 构建精细化的系统提示词
    3. 调用LLM生成测试用例
    4. 解析并验证JSON格式
    5. 更新状态
    """
    llm = create_llm(temperature=0.3)  # 降低温度以提高一致性

    # 获取用户的需求
    user_message = state["messages"][-1] if state["messages"] else None
    if not user_message:
        state["messages"].append(AIMessage(content="错误：未收到用户需求"))
        return state

    # 构建精细化的系统提示词
    system_prompt = """你是一个资深的测试工程师和QA专家。你的任务是根据用户需求生成高质量、可执行的测试用例。

【核心要求】
1. 每个测试用例必须包含以下7个字段，不能缺少任何字段
2. 测试用例必须具有可执行性和可验证性
3. 测试步骤必须清晰、详细、可重复
4. 预期结果必须明确、可量化、可验证
5. 优先级和类型必须合理分配

【字段说明】
- 用例ID: 唯一标识符，格式为TC+数字（如TC001、TC002）
- 用例标题: 简洁明了，能准确描述测试目的（20字以内）
- 前置条件: 执行测试前需要满足的条件，可以是系统状态、数据准备等
- 测试步骤: 详细的操作步骤，每步一行，使用"1. 2. 3."格式，步骤必须清晰可执行
- 预期结果: 执行测试后应该得到的结果，必须明确、可验证
- 优先级: 只能是"高"、"中"或"低"，根据功能重要性和风险程度判断
- 用例类型: 只能是"功能测试"、"性能测试"、"安全测试"、"兼容性测试"、"集成测试"或"回归测试"

【质量标准】
✓ 测试步骤具体明确，不使用模糊词汇（如"适当"、"大约"等）
✓ 每个测试用例只测试一个功能点
✓ 前置条件和测试步骤逻辑清晰，不存在循环依赖
✓ 预期结果可以通过自动化或手工验证
✓ 用例之间没有重复或冗余

【输出格式】
必须返回一个JSON数组，每个元素是一个测试用例对象。
示例：
[
    {
        "用例ID": "TC001",
        "用例标题": "正常登录测试",
        "前置条件": "1. 系统已启动\n2. 用户已注册，用户名为admin，密码为123456",
        "测试步骤": "1. 打开登录页面\n2. 在用户名输入框输入admin\n3. 在密码输入框输入123456\n4. 点击登录按钮",
        "预期结果": "1. 登录成功\n2. 页面跳转到首页\n3. 显示用户名admin",
        "优先级": "高",
        "用例类型": "功能测试"
    },
    {
        "用例ID": "TC002",
        "用例标题": "错误密码登录测试",
        "前置条件": "1. 系统已启动\n2. 用户已注册，用户名为admin，正确密码为123456",
        "测试步骤": "1. 打开登录页面\n2. 在用户名输入框输入admin\n3. 在密码输入框输入错误密码\n4. 点击登录按钮",
        "预期结果": "1. 登录失败\n2. 页面显示错误提示信息\n3. 页面停留在登录页面",
        "优先级": "高",
        "用例类型": "功能测试"
    }
]

现在，请根据用户需求生成测试用例。确保每个测试用例都符合上述要求。"""

    # 调用大模型
    messages = state["messages"] + [HumanMessage(content=system_prompt)]
    response = llm.invoke(messages)

    # 解析响应中的JSON
    test_cases = []
    try:
        # 尝试从响应中提取JSON
        content = response.content if hasattr(response, 'content') else str(response)
        # 查找JSON数组
        start_idx = content.find('[')
        end_idx = content.rfind(']') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            test_cases = json.loads(json_str)

            # 验证测试用例格式
            if not isinstance(test_cases, list):
                raise ValueError("返回的不是数组格式")

            if len(test_cases) == 0:
                raise ValueError("返回的测试用例列表为空")

            # 验证每个测试用例的字段
            for idx, case in enumerate(test_cases):
                if not isinstance(case, dict):
                    raise ValueError(f"第{idx+1}个测试用例不是字典格式")

                # 检查必需字段
                missing_fields = [f for f in REQUIRED_FIELDS if f not in case]
                if missing_fields:
                    raise ValueError(f"第{idx+1}个测试用例缺少字段: {', '.join(missing_fields)}")

                # 验证优先级
                if case.get("优先级") not in PRIORITY_LEVELS:
                    raise ValueError(f"第{idx+1}个测试用例的优先级无效: {case.get('优先级')}")

                # 验证用例类型
                if case.get("用例类型") not in TEST_CASE_TYPES:
                    raise ValueError(f"第{idx+1}个测试用例的类型无效: {case.get('用例类型')}")
        else:
            raise ValueError("响应中未找到JSON数组")

    except (json.JSONDecodeError, ValueError) as e:
        # 如果解析失败，返回错误消息
        error_msg = f"生成测试用例失败: {str(e)}"
        state["messages"].append(AIMessage(content=error_msg))
        state["review_feedback"] = error_msg
        return state

    # 更新状态
    state["test_cases"] = test_cases
    state["messages"].append(response)
    state["review_feedback"] = ""

    # 确保review_count被初始化（如果还没有的话）
    if "review_count" not in state:
        state["review_count"] = 0

    return state


def review_test_case_node(state: TestCaseState) -> TestCaseState:
    """
    节点2：评审测试用例
    检查生成的测试用例是否符合质量标准

    流程：
    1. 检查测试用例是否存在
    2. 构建严格的评审提示词
    3. 调用LLM进行评审
    4. 解析评审结果
    5. 更新状态和反馈信息
    """
    llm = create_llm(temperature=0.2)  # 使用更低的温度以提高评审的一致性

    if not state["test_cases"]:
        state["review_passed"] = False
        state["review_feedback"] = "错误：没有测试用例可以评审"
        return state

    # 构建严格的评审提示词
    review_prompt = f"""你是一个资深的QA评审专家。请严格评审以下测试用例，确保它们符合企业级质量标准。

【评审标准】
1. 字段完整性：每个用例必须包含所有7个必需字段
2. 字段有效性：
   - 用例ID必须唯一且格式正确（TC+数字）
   - 用例标题必须清晰明确（20字以内）
   - 前置条件必须完整、可重复
   - 测试步骤必须详细、清晰、可执行（不能有模糊词汇）
   - 预期结果必须明确、可验证
   - 优先级必须是"高"、"中"或"低"
   - 用例类型必须是"功能测试"、"性能测试"、"安全测试"、"兼容性测试"、"集成测试"或"回归测试"
3. 逻辑合理性：
   - 每个用例只测试一个功能点
   - 前置条件和测试步骤逻辑清晰
   - 没有循环依赖
4. 可执行性：
   - 测试步骤具体明确，可以被自动化或手工执行
   - 预期结果可以被验证
5. 无重复性：用例之间没有重复或冗余

【评审任务】
请评审以下测试用例：

{json.dumps(state["test_cases"], ensure_ascii=False, indent=2)}

【输出格式】
必须返回一个JSON对象，包含以下字段：
{{
    "passed": true/false,  // 是否通过评审
    "score": 0-100,  // 评审得分
    "issues": [  // 发现的问题列表
        {{
            "case_id": "TC001",  // 有问题的用例ID
            "field": "测试步骤",  // 有问题的字段
            "issue": "测试步骤过于模糊，使用了'适当'等不确定词汇",  // 问题描述
            "severity": "高"  // 问题严重程度：高/中/低
        }}
    ],
    "suggestions": [  // 改进建议列表
        "建议1",
        "建议2"
    ],
    "summary": "总体评价"  // 总体评价
}}

请严格按照上述格式返回评审结果。"""

    messages = state["messages"] + [HumanMessage(content=review_prompt)]
    response = llm.invoke(messages)

    # 解析评审结果
    review_passed = False
    review_feedback = ""
    try:
        content = response.content if hasattr(response, 'content') else str(response)
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            review_result = json.loads(json_str)

            # 获取评审结果
            review_passed = review_result.get("passed", False)
            score = review_result.get("score", 0)
            issues = review_result.get("issues", [])
            suggestions = review_result.get("suggestions", [])
            summary = review_result.get("summary", "")

            # 构建反馈信息
            feedback_parts = [f"评审得分: {score}/100"]
            if summary:
                feedback_parts.append(f"总体评价: {summary}")
            if issues:
                feedback_parts.append(f"发现{len(issues)}个问题:")
                for issue in issues:
                    if isinstance(issue, dict):
                        feedback_parts.append(f"  - [{issue.get('severity', '未知')}] {issue.get('case_id', 'N/A')}: {issue.get('issue', 'N/A')}")
                    else:
                        feedback_parts.append(f"  - {issue}")
            if suggestions:
                feedback_parts.append("改进建议:")
                for suggestion in suggestions:
                    feedback_parts.append(f"  - {suggestion}")

            review_feedback = "\n".join(feedback_parts)
        else:
            review_feedback = "无法解析评审结果"
            review_passed = False
    except (json.JSONDecodeError, ValueError) as e:
        review_feedback = f"评审结果解析失败: {str(e)}"
        review_passed = False

    # 增加评审次数
    if "review_count" not in state:
        state["review_count"] = 0
    state["review_count"] += 1
    state["review_passed"] = review_passed
    state["review_feedback"] = review_feedback
    state["messages"].append(response)

    return state


def save_test_case_node(state: TestCaseState) -> TestCaseState:
    """
    节点3：保存测试用例到Excel文件

    流程：
    1. 检查测试用例是否存在
    2. 生成时间戳文件名
    3. 调用save_test_cases_to_excel工具
    4. 更新状态
    """
    if not state["test_cases"]:
        state["file_path"] = ""
        state["messages"].append(AIMessage(content="错误：没有测试用例可以保存"))
        return state

    # 生成文件名（包含时间戳和评审次数信息）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"data/test_cases_{timestamp}.xlsx"

    # 确保目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 保存到Excel
    # save_test_cases_to_excel 是一个 @tool 装饰的函数，需要调用其底层函数
    try:
        result = save_test_cases_to_excel.invoke({
            "test_cases": state["test_cases"],
            "file_path": file_path,
            "sheet_name": "测试用例"
        })
    except Exception as e:
        result = f"保存失败: {str(e)}"

    state["file_path"] = file_path

    # 构建保存成功的消息
    save_message = f"""测试用例已保存！
文件路径: {file_path}
测试用例数量: {len(state["test_cases"])}
评审次数: {state["review_count"]}
评审状态: {'通过' if state["review_passed"] else '强制保存（超过最大评审次数）'}
{result}"""

    state["messages"].append(AIMessage(content=save_message))

    return state


# ============================================================================
# 条件边定义
# ============================================================================

def review_condition_edge(state: TestCaseState) -> str:
    """
    条件边：根据评审结果决定下一步

    决策逻辑：
    - 如果通过评审 → 返回"save_node"（保存）
    - 如果评审次数 >= MAX_REVIEW_COUNT → 返回"save_node"（强制保存，防止无限循环）
    - 否则 → 返回"write_node"（重新生成）

    Args:
        state: 当前状态

    Returns:
        str: 下一个节点的名称
    """
    # 检查是否通过评审
    if state["review_passed"]:
        return "save_node"

    # 检查是否达到最大评审次数
    if state["review_count"] >= MAX_REVIEW_COUNT:
        return "save_node"

    # 否则重新生成
    return "write_node"


# ============================================================================
# 构建工作流
# ============================================================================

def create_test_case_agent():
    """
    创建测试用例生成Agent

    工作流程：
    START
      ↓
    write_node (编写测试用例)
      ↓
    review_node (评审测试用例)
      ↓
    review_condition_edge (条件判断)
      ├─ 通过评审 → save_node
      ├─ 评审次数 >= MAX_REVIEW_COUNT → save_node
      └─ 否则 → write_node (循环)
      ↓
    save_node (保存到Excel)
      ↓
    END

    Returns:
        CompiledGraph: 编译后的工作流图
    """
    # 创建状态图
    agent_builder = StateGraph(TestCaseState)

    # 添加节点
    agent_builder.add_node("write_node", write_test_case_node)
    agent_builder.add_node("review_node", review_test_case_node)
    agent_builder.add_node("save_node", save_test_case_node)

    # 添加边
    agent_builder.add_edge(START, "write_node")
    agent_builder.add_edge("write_node", "review_node")

    # 添加条件边：根据评审结果决定下一步
    agent_builder.add_conditional_edges(
        "review_node",
        review_condition_edge,
        {
            "save_node": "save_node",
            "write_node": "write_node"
        }
    )

    agent_builder.add_edge("save_node", END)

    # 编译图
    graph = agent_builder.compile()

    return graph


# ============================================================================
# 主程序入口
# ============================================================================

def run_test_case_generator(requirement: str) -> Dict[str, Any]:
    """
    运行测试用例生成系统

    这是系统的主入口函数，用于生成、评审和保存测试用例。

    Args:
        requirement: 测试需求描述，应该包含：
            - 功能描述
            - 需要覆盖的场景
            - 特殊要求（如果有）

    Returns:
        Dict[str, Any]: 包含以下字段的字典：
            - test_cases: 生成的测试用例列表
            - file_path: 保存的Excel文件路径
            - review_count: 评审次数
            - review_passed: 是否通过评审
            - review_feedback: 最后一次的评审反馈

    Example:
        >>> requirement = "请为登录功能生成测试用例"
        >>> result = run_test_case_generator(requirement)
        >>> print(f"生成了 {len(result['test_cases'])} 个测试用例")
        >>> print(f"保存到: {result['file_path']}")
    """
    # 创建Agent
    graph = create_test_case_agent()

    # 初始化状态
    initial_state: TestCaseState = {
        "messages": [HumanMessage(content=requirement)],
        "test_cases": [],
        "review_count": 0,
        "review_passed": False,
        "file_path": "",
        "review_feedback": ""
    }

    # 执行工作流
    result = graph.invoke(initial_state)

    return {
        "test_cases": result["test_cases"],
        "file_path": result["file_path"],
        "review_count": result["review_count"],
        "review_passed": result["review_passed"],
        "review_feedback": result.get("review_feedback", "")
    }


if __name__ == "__main__":
    # 示例：生成登录功能的测试用例
    requirement = """
    请为一个用户登录功能生成测试用例。

    功能描述：
    用户可以通过输入用户名和密码登录系统。系统需要验证用户信息，
    并在登录成功后跳转到首页。

    需要覆盖的场景：
    1. 正常登录（用户名和密码都正确）
    2. 错误密码（用户存在但密码错误）
    3. 用户不存在（用户名不存在）
    4. 空输入（用户名或密码为空）
    5. SQL注入攻击（输入特殊字符）

    特殊要求：
    - 每个场景至少生成一个测试用例
    - 优先级应该根据功能重要性合理分配
    - 测试步骤必须清晰可执行
    """

    print("=" * 80)
    print("测试用例生成系统 - 开始执行")
    print("=" * 80)

    result = run_test_case_generator(requirement)

    print("\n" + "=" * 80)
    print("执行结果")
    print("=" * 80)
    print(f"✓ 生成的测试用例数量: {len(result['test_cases'])}")
    print(f"✓ 文件保存路径: {result['file_path']}")
    print(f"✓ 评审次数: {result['review_count']}")
    print(f"✓ 是否通过评审: {'是' if result['review_passed'] else '否'}")

    if result['review_feedback']:
        print(f"\n评审反馈:\n{result['review_feedback']}")

    if result['test_cases']:
        print(f"\n生成的测试用例:")
        for idx, case in enumerate(result['test_cases'], 1):
            print(f"\n  {idx}. {case.get('用例ID', 'N/A')} - {case.get('用例标题', 'N/A')}")
            print(f"     优先级: {case.get('优先级', 'N/A')}")
            print(f"     类型: {case.get('用例类型', 'N/A')}")
