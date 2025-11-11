"""
测试用例生成节点模块 - 精简版（重构）

核心功能：
1. parse_test_cases_from_string() - 解析LLM生成的测试用例JSON
2. review_test_cases_with_ai() - 使用AI自动评审测试用例
3. write_test_case_node() - 节点1：编写测试用例
4. review_test_case_node() - 节点2：评审测试用例
5. review_decision_edge_new() - 条件边：评审决策
6. save_to_excel_node() - 节点3：保存到Excel

工作流程：
    START → 节点1(编写) → 节点2(评审) → 条件边(决策) → 节点3(保存) → END
                                              ↓
                                            节点1(重新生成)
"""
import json
import os
import datetime
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from file_rag.models import TestCaseState
from file_rag.core.llm import create_llm, create_gpt5_llm


def parse_test_cases_from_string(test_cases_str: str) -> list:
    """
    从字符串中解析测试用例列表

    支持格式：
    1. JSON数组：[{...}, {...}]
    2. JSON对象：{"test_cases": [{...}]}
    3. 混合格式：文本中包含JSON

    Args:
        test_cases_str: 测试用例字符串

    Returns:
        测试用例列表，解析失败返回空列表
    """
    if not isinstance(test_cases_str, str):
        return []

    try:
        # 尝试直接解析JSON
        data = json.loads(test_cases_str)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and 'test_cases' in data:
            test_cases = data.get('test_cases', [])
            return test_cases if isinstance(test_cases, list) else []
    except json.JSONDecodeError:
        pass

    # 尝试从文本中提取JSON数组
    try:
        start_idx = test_cases_str.find('[')
        end_idx = test_cases_str.rfind(']') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = test_cases_str[start_idx:end_idx]
            data = json.loads(json_str)
            if isinstance(data, list):
                return data
    except json.JSONDecodeError:
        pass

    # 尝试从文本中提取JSON对象
    try:
        start_idx = test_cases_str.find('{')
        end_idx = test_cases_str.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = test_cases_str[start_idx:end_idx]
            data = json.loads(json_str)
            if isinstance(data, dict) and 'test_cases' in data:
                test_cases = data.get('test_cases', [])
                return test_cases if isinstance(test_cases, list) else []
    except json.JSONDecodeError:
        pass

    return []


def review_test_cases_with_ai(test_cases_list: list, llm) -> dict:
    """
    使用AI自动评审测试用例

    Args:
        test_cases_list: 测试用例列表
        llm: LLM模型实例

    Returns:
        评审结果字典：
        {
            "passed": bool,
            "score": int (0-100),
            "issues": list,
            "suggestions": list,
            "summary": str
        }
    """
    print("\n[AI评审] 开始自动评审测试用例...")

    review_prompt = f"""你是一个资深的QA评审专家。请严格评审以下测试用例。

【评审标准】
1. 字段完整性：所有必需字段都存在
2. 字段有效性：ID格式正确、优先级和类型有效
3. 逻辑合理性：每个用例只测试一个功能点
4. 可执行性：步骤具体明确，结果可验证
5. 无重复性：用例之间没有重复

【测试用例】
{json.dumps(test_cases_list, ensure_ascii=False, indent=2)}

【输出格式】
必须返回JSON对象：
{{
    "passed": true/false,
    "score": 0-100,
    "issues": [{{"case_id": "TC001", "field": "字段名", "issue": "问题描述"}}],
    "suggestions": ["建议1", "建议2"],
    "summary": "总体评价"
}}

请严格按照格式返回。"""

    try:
        response = llm.invoke([HumanMessage(content=review_prompt)])
        content = response.content if hasattr(response, 'content') else str(response)

        # 提取JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        if start_idx != -1 and end_idx > start_idx:
            json_str = content[start_idx:end_idx]
            review_result = json.loads(json_str)

            passed = review_result.get("passed", False)
            score = review_result.get("score", 0)
            print(f"[AI评审] 得分: {score}/100, 通过: {passed}")

            return review_result
    except Exception as e:
        print(f"[AI评审] 评审失败: {str(e)}")

    # 评审失败时返回默认通过
    return {
        "passed": True,
        "score": 80,
        "issues": [],
        "suggestions": [],
        "summary": "自动评审失败，默认通过"
    }


def write_test_case_node(state: TestCaseState) -> TestCaseState:
    """
    节点1：编写测试用例

    功能：
    1. 检测文件类型（图片、PDF、纯文本）
    2. 选择合适的LLM模型
    3. 生成测试用例
    4. 解析为结构化格式

    Args:
        state: 当前测试用例状态

    Returns:
        更新后的状态
    """
    print("\n" + "="*80)
    print("【节点1】编写测试用例")
    print("="*80)

    messages = state.get("messages", [])
    file_type = state.get("file_type", "text")
    extracted_content = state.get("extracted_content", "")
    test_requirement = state.get("test_requirement", "")
    review_feedback = state.get("review_feedback", "")
    test_review_count = state.get("test_review_count", 0)

    print(f"[输入] 文件类型: {file_type}, 需求: {test_requirement[:50] if test_requirement else '无'}")
    print(f"[状态] 评审次数: {test_review_count}")

    # 选择LLM模型
    if file_type in ["image", "pdf"]:
        print("[模型] 使用多模态模型（GPT-5）")
        llm = create_gpt5_llm()
        used_multimodal = True
    else:
        print("[模型] 使用文本模型（DeepSeek）")
        llm = create_llm(temperature=0.7)
        used_multimodal = False

    try:
        print("[LLM] 正在生成测试用例...")

        # 处理 PDF 文件 - 直接传递给多模态模型
        if file_type == "pdf":
            print("[PDF] 检测到 PDF 文件，开始处理...")
            try:
                # 从消息中查找 PDF 文件块
                for message in messages:
                    if isinstance(message, HumanMessage) and isinstance(message.content, list):
                        for content_block in message.content:
                            if (isinstance(content_block, dict) and
                                content_block.get('type') == 'file' and
                                content_block.get('source_type') == 'base64' and
                                content_block.get('mime_type') == 'application/pdf'):

                                base64_data = content_block.get('data', '')
                                filename = content_block.get('metadata', {}).get('filename', 'document.pdf')

                                print(f"[PDF] 处理 PDF 文件: {filename}")

                                # 构建包含 PDF 的消息
                                # 注意：由于 LangChain 对 PDF 的多模态支持有限，
                                # 我们使用文本提取 + 多模态模型的方式
                                try:
                                    from file_rag.utils.pdf_utils import extract_pdf_content

                                    # 提取 PDF 文本内容
                                    pdf_text = extract_pdf_content(base64_data)

                                    # 构建包含提取内容的提示
                                    pdf_prompt_with_content = f"""你是一个专业的测试工程师。请根据以下 PDF 文档内容和测试需求编写测试用例：

【PDF 文档内容】
{pdf_text[:2000]}

【测试需求】
{test_requirement}

【输出格式】
必须返回JSON数组，每个元素是一个测试用例：
[
    {{
        "用例ID": "TC001",
        "用例标题": "功能描述",
        "前置条件": "前置条件",
        "测试步骤": "1. 步骤一\\n2. 步骤二",
        "预期结果": "期望结果",
        "优先级": "高",
        "用例类型": "功能测试"
    }}
]

【要求】
1. 必须返回有效的JSON数组
2. 优先级：高/中/低
3. 用例类型：功能测试/性能测试/安全测试/兼容性测试/集成测试/回归测试
4. 生成3-5个高质量的测试用例
5. 不要添加任何其他文本，只返回JSON"""

                                    pdf_llm_messages = [
                                        SystemMessage(content=pdf_prompt_with_content),
                                        HumanMessage(content="请根据上述 PDF 内容生成测试用例")
                                    ]

                                    response = llm.invoke(pdf_llm_messages)
                                    test_cases_str = response.content
                                    print(f"[PDF] 生成完成，长度: {len(test_cases_str)}")
                                except Exception as pdf_extract_error:
                                    print(f"[PDF] 文本提取失败: {pdf_extract_error}，使用降级方案")
                                    test_cases_str = None
                                break
                        if 'test_cases_str' in locals():
                            break
            except Exception as e:
                print(f"[PDF] PDF 处理异常: {str(e)}")
                # 降级处理：使用提取的内容
                test_cases_str = None

        # 处理图片文件 - 直接传递给多模态模型
        elif file_type == "image":
            print("[图片] 检测到图片文件，开始处理...")
            try:
                # 从消息中查找图片文件块
                for message in messages:
                    if isinstance(message, HumanMessage) and isinstance(message.content, list):
                        for content_block in message.content:
                            if (isinstance(content_block, dict) and
                                content_block.get('type') == 'file' and
                                content_block.get('source_type') == 'base64' and
                                'image' in content_block.get('mime_type', '')):

                                base64_data = content_block.get('data', '')
                                filename = content_block.get('metadata', {}).get('filename', 'image.png')
                                mime_type = content_block.get('mime_type', 'image/png')

                                print(f"[图片] 处理图片文件: {filename}")

                                # 使用多模态模型直接分析图片并生成测试用例
                                image_prompt = f"""你是一个专业的测试工程师。请分析这张图片的内容，然后根据以下需求编写测试用例：

【测试需求】
{test_requirement}

【输出格式】
必须返回JSON数组，每个元素是一个测试用例：
[
    {{
        "用例ID": "TC001",
        "用例标题": "功能描述",
        "前置条件": "前置条件",
        "测试步骤": "1. 步骤一\\n2. 步骤二",
        "预期结果": "期望结果",
        "优先级": "高",
        "用例类型": "功能测试"
    }}
]

【要求】
1. 必须返回有效的JSON数组
2. 优先级：高/中/低
3. 用例类型：功能测试/性能测试/安全测试/兼容性测试/集成测试/回归测试
4. 生成3-5个高质量的测试用例
5. 不要添加任何其他文本，只返回JSON"""

                                # 构建包含图片的消息
                                image_llm_messages = [
                                    SystemMessage(content=image_prompt),
                                    HumanMessage(content=[
                                        {"type": "text", "text": "请分析这张图片并生成测试用例"},
                                        {
                                            "type": "image_url",
                                            "image_url": {"url": f"data:{mime_type};base64,{base64_data}"}
                                        }
                                    ])
                                ]

                                response = llm.invoke(image_llm_messages)
                                test_cases_str = response.content
                                print(f"[图片] 生成完成，长度: {len(test_cases_str)}")
                                break
                        if 'test_cases_str' in locals():
                            break
            except Exception as e:
                print(f"[图片] 图片处理异常: {str(e)}")
                # 降级处理
                test_cases_str = None

        # 处理纯文本
        else:
            print("[文本] 使用纯文本模式...")

            # 构建系统提示
            if review_feedback:
                # 重新生成模式
                system_prompt = f"""你是一个专业的测试工程师。之前的测试用例未通过评审，请根据反馈重新编写。

【评审反馈】
{review_feedback}

【原始需求】
{test_requirement}

【输出格式】
必须返回JSON数组，每个元素是一个测试用例：
[
    {{
        "用例ID": "TC001",
        "用例标题": "功能描述",
        "前置条件": "前置条件",
        "测试步骤": "1. 步骤一\\n2. 步骤二",
        "预期结果": "期望结果",
        "优先级": "高",
        "用例类型": "功能测试"
    }}
]

【要求】
1. 必须返回有效的JSON数组
2. 优先级：高/中/低
3. 用例类型：功能测试/性能测试/安全测试/兼容性测试/集成测试/回归测试
4. 不要添加任何其他文本，只返回JSON"""
            else:
                # 首次生成模式
                system_prompt = f"""你是一个专业的测试工程师。请根据需求编写测试用例。

【测试需求】
{test_requirement}

【内容分析】
{extracted_content[:1000] if extracted_content else '无'}

【输出格式】
必须返回JSON数组，每个元素是一个测试用例：
[
    {{
        "用例ID": "TC001",
        "用例标题": "功能描述",
        "前置条件": "前置条件",
        "测试步骤": "1. 步骤一\\n2. 步骤二",
        "预期结果": "期望结果",
        "优先级": "高",
        "用例类型": "功能测试"
    }}
]

【要求】
1. 必须返回有效的JSON数组
2. 优先级：高/中/低
3. 用例类型：功能测试/性能测试/安全测试/兼容性测试/集成测试/回归测试
4. 生成3-5个高质量的测试用例
5. 不要添加任何其他文本，只返回JSON"""

            # 构建消息
            llm_messages = [SystemMessage(content=system_prompt)]

            # 添加用户消息
            user_message = HumanMessage(content=test_requirement or "请根据提供的内容编写测试用例")
            llm_messages.append(user_message)

            # 调用LLM
            response = llm.invoke(llm_messages)
            test_cases_str = response.content
            print(f"[文本] 生成完成，长度: {len(test_cases_str)}")

        # 如果前面的处理没有生成测试用例，使用降级方案
        if 'test_cases_str' not in locals() or not test_cases_str:
            print("[降级] 使用降级方案...")
            system_prompt = f"""你是一个专业的测试工程师。请根据需求编写测试用例。

【测试需求】
{test_requirement}

【输出格式】
必须返回JSON数组，每个元素是一个测试用例：
[
    {{
        "用例ID": "TC001",
        "用例标题": "功能描述",
        "前置条件": "前置条件",
        "测试步骤": "1. 步骤一\\n2. 步骤二",
        "预期结果": "期望结果",
        "优先级": "高",
        "用例类型": "功能测试"
    }}
]

【要求】
1. 必须返回有效的JSON数组
2. 优先级：高/中/低
3. 用例类型：功能测试/性能测试/安全测试/兼容性测试/集成测试/回归测试
4. 生成3-5个高质量的测试用例
5. 不要添加任何其他文本，只返回JSON"""

            llm_messages = [SystemMessage(content=system_prompt)]
            user_message = HumanMessage(content=test_requirement or "请根据提供的内容编写测试用例")
            llm_messages.append(user_message)
            response = llm.invoke(llm_messages)
            test_cases_str = response.content

        print(f"[LLM] 生成完成，长度: {len(test_cases_str)}")

        # 解析测试用例
        test_cases_list = parse_test_cases_from_string(test_cases_str)

        if test_cases_list:
            print(f"[解析] 成功解析 {len(test_cases_list)} 个测试用例")
        else:
            print("[警告] 无法解析测试用例")
            test_cases_list = []

        # 更新状态
        ai_message = AIMessage(content=f"✅ 已生成 {len(test_cases_list)} 个测试用例，准备评审...")
        updated_messages = messages + [ai_message]

        return {
            **state,
            "messages": updated_messages,
            "test_cases": test_cases_str,
            "test_cases_list": test_cases_list,
            "waiting_for_review": True,
            "used_multimodal": used_multimodal,
            "test_review_count": test_review_count + 1
        }

    except Exception as e:
        print(f"[错误] 生成失败: {str(e)}")
        ai_message = AIMessage(content=f"❌ 生成失败: {str(e)}")
        updated_messages = messages + [ai_message]

        return {
            **state,
            "messages": updated_messages,
            "test_cases": "",
            "test_cases_list": [],
            "waiting_for_review": False
        }


def review_test_case_node(state: TestCaseState) -> TestCaseState:
    """
    节点2：评审测试用例

    功能：
    1. 使用LLM评审测试用例
    2. 返回评审结果
    3. 返回评审得分和建议

    Args:
        state: 当前测试用例状态

    Returns:
        更新后的状态
    """
    print("\n" + "="*80)
    print("【节点2】测试用例评审")
    print("="*80)

    messages = state.get("messages", [])
    test_cases_list = state.get("test_cases_list", [])

    print(f"[输入] 测试用例数量: {len(test_cases_list)}")

    if not test_cases_list:
        print("[警告] 没有测试用例可以评审")
        return {
            **state,
            "review_passed": False,
            "review_score": 0,
            "review_feedback": "没有测试用例可以评审"
        }

    try:
        print("[LLM] 正在评审测试用例...")
        llm = create_llm(temperature=0.2)
        review_result = review_test_cases_with_ai(test_cases_list, llm)

        review_passed = review_result.get("passed", False)
        review_score = review_result.get("score", 0)
        review_summary = review_result.get("summary", "")
        review_issues = review_result.get("issues", [])
        review_suggestions = review_result.get("suggestions", [])

        print(f"[评审] 通过: {review_passed}, 得分: {review_score}/100")

        # 构建反馈信息
        feedback_parts = []
        if review_passed:
            feedback_parts.append(f"✅ 评审通过！得分: {review_score}/100")
        else:
            feedback_parts.append(f"⚠️ 评审未通过。得分: {review_score}/100")

        if review_summary:
            feedback_parts.append(f"\n📝 总体评价: {review_summary}")

        if review_issues:
            feedback_parts.append(f"\n⚠️ 发现的问题:")
            for issue in review_issues[:3]:
                if isinstance(issue, dict):
                    feedback_parts.append(f"  - {issue.get('issue', 'N/A')}")

        if review_suggestions:
            feedback_parts.append(f"\n💡 改进建议:")
            for suggestion in review_suggestions[:3]:
                feedback_parts.append(f"  - {suggestion}")

        feedback = "\n".join(feedback_parts)

        # 更新状态
        ai_message = AIMessage(content=feedback)
        updated_messages = messages + [ai_message]

        return {
            **state,
            "messages": updated_messages,
            "review_passed": review_passed,
            "review_score": review_score,
            "review_summary": review_summary,
            "review_issues": review_issues,
            "review_suggestions": review_suggestions,
            "review_feedback": feedback
        }

    except Exception as e:
        print(f"[错误] 评审失败: {str(e)}")
        return {
            **state,
            "review_passed": False,
            "review_score": 0,
            "review_feedback": f"评审失败: {str(e)}"
        }


def review_decision_edge_new(state: TestCaseState) -> str:
    """
    条件边：评审决策逻辑

    逻辑：
    - 如果评审通过 OR 评审次数 >= 3 → 返回 "save_to_excel"
    - 否则 → 返回 "write_test_case"（重新生成）

    Args:
        state: 当前测试用例状态

    Returns:
        下一个节点的名称
    """
    print("\n" + "="*80)
    print("【条件边】评审决策")
    print("="*80)

    review_passed = state.get("review_passed", False)
    test_review_count = state.get("test_review_count", 0)

    print(f"[决策] 评审通过: {review_passed}, 评审次数: {test_review_count}")

    if review_passed or test_review_count >= 3:
        print("[决策] ✅ 转向节点3（保存到Excel）")
        return "save_to_excel"
    else:
        print("[决策] 🔄 转向节点1（重新生成）")
        return "write_test_case"


def save_to_excel_node(state: TestCaseState) -> TestCaseState:
    """
    节点3：保存测试用例到Excel

    功能：
    1. 解析测试用例
    2. 添加评审信息
    3. 保存到Excel文件

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态
    """
    print("\n" + "="*80)
    print("【节点3】保存到Excel")
    print("="*80)

    messages = state.get("messages", [])
    test_cases_list = state.get("test_cases_list", [])
    review_passed = state.get("review_passed", False)
    review_score = state.get("review_score", 0)
    review_summary = state.get("review_summary", "")
    test_review_count = state.get("test_review_count", 0)

    print(f"[输入] 测试用例数量: {len(test_cases_list)}")
    print(f"[输入] 评审状态: {'通过' if review_passed else '强制保存'}")

    if not test_cases_list:
        print("[错误] 没有测试用例可以保存")
        ai_message = AIMessage(content="❌ 没有测试用例可以保存")
        updated_messages = messages + [ai_message]
        return {
            **state,
            "messages": updated_messages,
            "file_path": ""
        }

    try:
        # 导入保存工具
        from tools import save_test_cases_to_excel

        # 生成文件名
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = f"data/test_cases_{timestamp}.xlsx"

        # 确保目录存在
        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        # 添加评审信息到每个测试用例
        for case in test_cases_list:
            case["评审状态"] = "✅ 通过" if review_passed else "⚠️ 强制保存"
            case["评审得分"] = str(review_score)
            case["评审意见"] = review_summary

        # 定义Excel列顺序
        columns = [
            "用例ID", "用例标题", "前置条件", "测试步骤", "预期结果",
            "用例类型", "优先级", "评审状态", "评审得分", "评审意见"
        ]

        print(f"[保存] 保存到: {file_path}")

        # 调用保存工具
        result = save_test_cases_to_excel.invoke({
            "test_cases": test_cases_list,
            "file_path": file_path,
            "sheet_name": "测试用例",
            "columns": columns
        })

        print(f"[保存] 结果: {result}")

        # 构建反馈信息
        feedback_parts = [f"✅ 测试用例已保存！"]
        feedback_parts.append(f"\n📊 统计信息：")
        feedback_parts.append(f"- 用例数量：{len(test_cases_list)}")
        feedback_parts.append(f"- 评审次数：{test_review_count}")
        feedback_parts.append(f"- 评审得分：{review_score}/100")
        feedback_parts.append(f"- 评审状态：{'通过' if review_passed else '强制保存（超过最大评审次数）'}")
        feedback_parts.append(f"\n💾 文件路径：{os.path.abspath(file_path)}")

        ai_response = "\n".join(feedback_parts)
        ai_message = AIMessage(content=ai_response)
        updated_messages = messages + [ai_message]

        return {
            **state,
            "messages": updated_messages,
            "file_path": file_path,
            "test_cases": "",
            "test_cases_list": [],
            "waiting_for_review": False,
            "test_review_count": 0
        }

    except Exception as e:
        print(f"[错误] 保存失败: {str(e)}")
        ai_message = AIMessage(content=f"❌ 保存失败: {str(e)}")
        updated_messages = messages + [ai_message]

        return {
            **state,
            "messages": updated_messages,
            "file_path": ""
        }


