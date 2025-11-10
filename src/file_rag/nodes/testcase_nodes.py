"""
测试用例生成节点模块
负责测试用例生成工作流的所有节点

注意：本模块主要使用 testcase_generation_bridge_node 作为统一的测试用例生成节点。
其他函数（generate_test_case_node等）是旧版工作流的节点，已被替代但保留以保持向后兼容性。
"""
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from file_rag.models import ConversationState, TestCaseGenerationState
from file_rag.core.llm import create_llm,create_gpt5_llm
from file_rag.utils.pdf_utils import extract_pdf_content, extract_pdf_images


def testcase_generation_bridge_node(state: ConversationState) -> ConversationState:
    """
    桥接节点：测试用例生成（支持人工评审）

    工作流程：
    1. 检测是否是用户评审输入（"通过"或"不通过"）
    2. 如果是评审输入：根据评审结果保存或重新生成
    3. 如果不是评审输入：生成新的测试用例并等待用户评审

    Args:
        state: 当前对话状态（ConversationState）

    Returns:
        更新后的状态，包含生成的测试用例和AI回复
    """
    print("\n=== 桥接节点：测试用例生成（人工评审模式）===")

    messages = state.get("messages", [])
    file_type = state.get("file_type", "text")
    extracted_content = state.get("extracted_content", "")

    # 获取状态中的测试用例相关信息
    test_cases = state.get("test_cases", "")
    test_review_count = state.get("test_review_count", 0)
    waiting_for_review = state.get("waiting_for_user_review", False)

    # 步骤1：检测是否是用户评审输入
    user_input = ""
    for msg in reversed(messages):
        if isinstance(msg, HumanMessage):
            user_input = msg.content
            break
        elif isinstance(msg, dict) and msg.get("type") == "human":
            content = msg.get("content", "")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "text":
                        user_input = item.get("text", "")
                        break
            elif isinstance(content, str):
                user_input = content
            if user_input:
                break

    print(f"[用户输入] {user_input[:100]}...")
    print(f"[等待评审] {waiting_for_review}")
    print(f"[已有测试用例] {bool(test_cases)}")

    # 步骤2：如果正在等待评审且用户输入了评审结果
    if waiting_for_review and test_cases:
        print("\n[模式] 处理用户评审")

        # 解析用户评审
        if "通过" in user_input and "不通过" not in user_input:
            print("[评审结果] ✅ 用户评审通过")

            # 保存测试用例到Excel
            from tools import save_test_cases_to_excel
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"test_cases_{timestamp}.xlsx"

            try:
                result = save_test_cases_to_excel.invoke({
                    "test_cases": test_cases,
                    "file_name": file_name
                })

                ai_response = f"""✅ 评审通过！测试用例已保存

📊 执行统计：
- 评审次数：{test_review_count + 1}
- 评审结果：通过

💾 保存结果：
{result}

📝 测试用例内容：

{test_cases}
"""
            except Exception as e:
                ai_response = f"❌ 保存失败：{str(e)}\n\n测试用例内容：\n{test_cases}"

            # 清除等待评审状态
            ai_message = AIMessage(content=ai_response)
            updated_messages = messages + [ai_message]

            return {
                **state,
                "messages": updated_messages,
                "waiting_for_user_review": False,
                "test_cases": "",
                "test_review_count": 0
            }

        else:
            print("[评审结果] ❌ 用户评审不通过")

            # 提取反馈意见
            feedback = user_input
            if "不通过" in user_input:
                parts = user_input.split("不通过", 1)
                if len(parts) > 1:
                    feedback = parts[1].strip().lstrip("，,：: ")

            print(f"[反馈意见] {feedback[:100]}...")

            # 获取原始分析结果和是否使用了多模态模型
            original_analysis = state.get("original_analysis", "")
            used_multimodal = state.get("used_multimodal", False)
            requirement = state.get("test_requirement", "")  # 提前获取 requirement

            print(f"[状态] 原始分析长度: {len(original_analysis)}, 使用多模态: {used_multimodal}")

            # 重新生成测试用例
            # 检测原始消息中是否有图片
            has_image = False
            original_message = None
            for msg in messages:
                if isinstance(msg, dict):
                    content = msg.get('content', '')
                    if isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict):
                                if item.get('type') == 'image_url':
                                    has_image = True
                                    original_message = msg
                                    break
                                elif item.get('type') == 'text' and "编写测试用例" in item.get('text', ''):
                                    original_message = msg
                if has_image:
                    break

            # 如果使用了多模态模型（图片或PDF），基于原始分析结果重新生成
            if used_multimodal and original_analysis:
                print(f"[检测] ✅ 使用了多模态模型，基于原始分析结果重新生成")

                # 如果有图片，使用豆包多模态模型
                if has_image and original_message:
                    print(f"[模型] 使用豆包多模态模型（图片）")
                    model = create_gpt5_llm()

                    system_prompt = f"""你是一个专业的测试工程师。之前生成的测试用例未通过评审，请根据评审反馈重新编写。

评审反馈：{feedback}

之前的分析和测试用例：
{original_analysis}

请仔细分析用户上传的图片，理解图片中展示的功能、界面或流程，然后根据评审反馈改进测试用例。

测试用例必须包含以下字段：
1. 用例编号（格式：TC001, TC002...）
2. 用例标题（简洁明了）
3. 前置条件（执行测试前需要满足的条件）
4. 测试步骤（详细的操作步骤，每步一行）
5. 预期结果（期望的测试结果）
6. 优先级（高/中/低）

请基于图片内容、之前的分析和评审反馈编写改进的测试用例。"""

                    # 使用原始消息（包含图片）
                    llm_messages = [SystemMessage(content=system_prompt), original_message]

                    response = model.invoke(llm_messages)
                    new_test_cases = response.content

                    print(f"[重新生成] 已使用豆包多模态模型重新生成测试用例（第 {test_review_count + 1} 次）")

                else:
                    # PDF 或其他多模态内容，使用 DeepSeek 基于原始分析结果
                    print(f"[模型] 使用 DeepSeek 模型（基于原始分析）")
                    model = create_llm()

                    system_prompt = """你是一个专业的测试工程师。之前生成的测试用例未通过评审，请根据评审反馈重新编写。

测试用例必须包含以下字段：
1. 用例编号（格式：TC001, TC002...）
2. 用例标题（简洁明了）
3. 前置条件（执行测试前需要满足的条件）
4. 测试步骤（详细的操作步骤，每步一行）
5. 预期结果（期望的测试结果）
6. 优先级（高/中/低）

请仔细阅读之前的分析和评审反馈，针对性地改进测试用例。"""

                    user_prompt = f"""{original_analysis}

评审反馈：{feedback}

请根据以上内容和反馈重新编写测试用例。"""

                    llm_messages = [
                        SystemMessage(content=system_prompt),
                        HumanMessage(content=user_prompt)
                    ]

                    response = model.invoke(llm_messages)
                    new_test_cases = response.content

                    print(f"[重新生成] 已基于原始分析重新生成测试用例（第 {test_review_count + 1} 次）")

            else:
                # 没有图片，使用DeepSeek模型
                print(f"[检测] 无图片，使用DeepSeek模型重新生成")

                # 提取原始需求（如果还没有）
                if not requirement:
                    # 从消息历史中提取
                    for msg in messages:
                        if isinstance(msg, dict):
                            content = msg.get('content', '')
                            if isinstance(content, str) and "编写测试用例" in content:
                                requirement = content
                                break
                            elif isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'text':
                                        text = item.get('text', '')
                                        if "编写测试用例" in text:
                                            requirement = text
                                            break
                        elif isinstance(msg, HumanMessage) and "编写测试用例" in msg.content:
                            requirement = msg.content
                            break

                # 调用大模型重新生成
                model = create_llm()

                system_prompt = """你是一个专业的测试工程师。之前生成的测试用例未通过评审，请根据评审反馈重新编写。

测试用例必须包含以下字段：
1. 用例编号（格式：TC001, TC002...）
2. 用例标题（简洁明了）
3. 前置条件（执行测试前需要满足的条件）
4. 测试步骤（详细的操作步骤，每步一行）
5. 预期结果（期望的测试结果）
6. 优先级（高/中/低）

请仔细阅读评审反馈，针对性地改进测试用例。"""

                user_prompt = f"""原始需求：{requirement}

评审反馈：{feedback}

请根据以上反馈重新编写测试用例。"""

                llm_messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_prompt)
                ]

                response = model.invoke(llm_messages)
                new_test_cases = response.content

                print(f"[重新生成] 已生成新的测试用例（第 {test_review_count + 1} 次）")

            ai_response = f"""✅ 已根据您的反馈重新生成测试用例（第 {test_review_count + 1} 次）：

{new_test_cases}

---

**请评审以上测试用例**：
- 如果符合要求，请回复：**通过**
- 如果需要修改，请回复：**不通过**，并说明改进意见

例如：
- "通过"
- "不通过，需要增加边界场景的测试用例"
"""

            ai_message = AIMessage(content=ai_response)
            updated_messages = messages + [ai_message]

            return {
                **state,
                "messages": updated_messages,
                "test_cases": new_test_cases,
                "test_review_count": test_review_count + 1,
                "waiting_for_user_review": True,
                "test_requirement": requirement
            }

    # 步骤3：首次生成测试用例
    print("\n[模式] 首次生成测试用例")

    # 获取文件类型和提取的内容
    file_type = state.get("file_type", "text")
    extracted_content = state.get("extracted_content", "")

    # 检测是否有 PDF 文件
    has_pdf = False
    pdf_base64_data = ""
    pdf_filename = ""

    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict):
                        if item.get('type') == 'file' and 'pdf' in item.get('mime_type', '').lower():
                            has_pdf = True
                            pdf_base64_data = item.get('data', '')
                            pdf_filename = item.get('metadata', {}).get('filename', 'unknown.pdf')
                            break
        elif isinstance(msg, HumanMessage) and isinstance(msg.content, list):
            for item in msg.content:
                if isinstance(item, dict):
                    if item.get('type') == 'file' and 'pdf' in item.get('mime_type', '').lower():
                        has_pdf = True
                        pdf_base64_data = item.get('data', '')
                        pdf_filename = item.get('metadata', {}).get('filename', 'unknown.pdf')
                        break
        if has_pdf:
            break

    # 如果有 PDF，先提取 PDF 内容（包括图片）
    if has_pdf and pdf_base64_data:
        print(f"[检测] ✅ 发现 PDF 文件：{pdf_filename}")
        print(f"[步骤1] 正在提取 PDF 文本内容...")

        # 提取 PDF 文本
        pdf_text = extract_pdf_content(pdf_base64_data)
        print(f"  提取的文本长度: {len(pdf_text)} 字符")

        # 提取 PDF 图片
        print(f"[步骤2] 正在提取 PDF 图片...")
        pdf_images = extract_pdf_images(pdf_base64_data)
        print(f"  提取了 {len(pdf_images)} 张图片")

        # 如果有图片，使用豆包模型识别
        image_descriptions = []
        if pdf_images:
            print(f"[步骤3] 使用豆包多模态模型识别 PDF 图片...")
            doubao_model = create_gpt5_llm()

            for idx, img_info in enumerate(pdf_images):
                print(f"  识别第 {idx + 1}/{len(pdf_images)} 张图片（第{img_info['page']}页）...")

                # 构建图片识别消息
                image_message = HumanMessage(content=[
                    {'type': 'text', 'text': '请详细描述这张图片的内容，包括图片中的文字、图表、图形等所有信息。'},
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f"data:image/{img_info['ext']};base64,{img_info['data']}"
                        }
                    }
                ])

                try:
                    img_response = doubao_model.invoke([image_message])
                    description = img_response.content
                    image_descriptions.append({
                        'page': img_info['page'],
                        'index': img_info['index'],
                        'description': description
                    })
                    print(f"    ✓ 图片识别成功: {description[:100]}...")
                except Exception as e:
                    print(f"    ✗ 图片识别失败: {e}")
                    image_descriptions.append({
                        'page': img_info['page'],
                        'index': img_info['index'],
                        'description': f"图片识别失败: {str(e)}"
                    })

        # 组合 PDF 内容
        combined_pdf_content = f"""PDF文件名: {pdf_filename}

【文本内容】
{pdf_text}
"""

        if image_descriptions:
            combined_pdf_content += "\n【图片内容】\n"
            for img_desc in image_descriptions:
                combined_pdf_content += f"\n图片 {img_desc['index']}（第{img_desc['page']}页）：\n{img_desc['description']}\n"

        # 更新 extracted_content
        extracted_content = combined_pdf_content
        print(f"[完成] PDF 内容提取完成（文本 + {len(image_descriptions)} 张图片）")

    # 检测是否有图片（非 PDF）
    has_image = False
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'image_url':
                        has_image = True
                        break
        if has_image:
            break

    # 提取测试需求（用于保存到状态）
    requirement = ""
    original_analysis = ""  # 保存原始分析结果
    used_multimodal = False  # 是否使用了多模态模型

    # 如果有图片，使用豆包多模态模型分析图片
    if has_image:
        print(f"[检测] ✅ 发现图片，使用豆包多模态模型分析")
        used_multimodal = True

        # 提取文本需求（用于记录）
        for msg in messages:
            if isinstance(msg, dict):
                content = msg.get('content', '')
                if isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            requirement += item.get('text', '') + "\n"
            elif isinstance(msg, HumanMessage):
                if isinstance(msg.content, list):
                    for item in msg.content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            requirement += item.get('text', '') + "\n"
        requirement = requirement.strip()
        print(f"[需求来源] 从用户消息提取（包含图片）")
        print(f"[测试需求] {requirement[:200]}...")

        # 使用豆包多模态模型
        model = create_gpt5_llm()

        # 构建系统提示
        system_prompt = """你是一个专业的测试工程师。请仔细分析用户上传的图片，理解图片中展示的功能、界面或流程，然后编写详细的测试用例。

测试用例必须包含以下字段：
1. 用例编号（格式：TC001, TC002...）
2. 用例标题（简洁明了）
3. 前置条件（执行测试前需要满足的条件）
4. 测试步骤（详细的操作步骤，每步一行）
5. 预期结果（期望的测试结果）
6. 优先级（高/中/低）

请先分析图片内容，说明你看到了什么功能或界面，然后基于图片内容编写测试用例。
确保测试用例覆盖正常场景、异常场景和边界场景。"""

        # 直接使用原始消息（包含图片）
        llm_messages = [SystemMessage(content=system_prompt)] + messages

        # 调用豆包多模态模型
        response = model.invoke(llm_messages)
        test_cases = response.content

        # 保存原始分析结果（包含图片分析）
        original_analysis = test_cases

        print(f"[生成] 已使用豆包多模态模型生成测试用例（第 1 次）")
        print(f"[预览] {test_cases[:200]}...")

    else:
        # 没有图片，使用DeepSeek模型
        print(f"[检测] 无图片，使用DeepSeek模型")

        # 提取测试需求（如果还没有提取）
        if extracted_content:
            requirement = f"根据以下内容编写测试用例：\n\n{extracted_content}"
            print(f"[需求来源] 从文件提取的内容（{file_type}）")
            # 如果有 extracted_content，说明可能是 PDF，标记为使用了多模态
            if "【图片内容】" in extracted_content:
                used_multimodal = True
        else:
            for msg in messages:
                if isinstance(msg, dict):
                    content = msg.get('content', '')
                    if isinstance(content, str):
                        requirement += content + "\n"
                    elif isinstance(content, list):
                        for item in content:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                requirement += item.get('text', '') + "\n"
                elif isinstance(msg, HumanMessage):
                    if isinstance(msg.content, str):
                        requirement += msg.content + "\n"
            print(f"[需求来源] 从用户消息提取")

        requirement = requirement.strip()
        print(f"[测试需求] {requirement[:200]}...")

        # 调用大模型生成测试用例
        model = create_llm()

        system_prompt = """你是一个专业的测试工程师。请根据用户的需求编写详细的测试用例。

测试用例必须包含以下字段：
1. 用例编号（格式：TC001, TC002...）
2. 用例标题（简洁明了）
3. 前置条件（执行测试前需要满足的条件）
4. 测试步骤（详细的操作步骤，每步一行）
5. 预期结果（期望的测试结果）
6. 优先级（高/中/低）

请以清晰的结构化格式输出测试用例，每个测试用例之间用空行分隔。
确保测试用例覆盖正常场景、异常场景和边界场景。"""

        user_prompt = f"测试需求：{requirement}"

        llm_messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]

        response = model.invoke(llm_messages)
        test_cases = response.content

        # 保存原始分析结果
        if extracted_content:
            # 如果有 extracted_content（PDF/图片提取的内容），保存它
            original_analysis = f"原始内容分析：\n{extracted_content}\n\n首次生成的测试用例：\n{test_cases}"
        else:
            # 纯文本，保存需求和测试用例
            original_analysis = f"原始需求：\n{requirement}\n\n首次生成的测试用例：\n{test_cases}"

        print(f"[生成] 已生成测试用例（第 1 次）")
        print(f"[预览] {test_cases[:200]}...")

    # 构建AI回复，提示用户评审
    ai_response = f"""✅ 已生成测试用例：

{test_cases}

---

**请评审以上测试用例**：
- 如果符合要求，请回复：**通过**
- 如果需要修改，请回复：**不通过**，并说明改进意见

例如：
- "通过"
- "不通过，需要增加边界场景的测试用例"
"""

    ai_message = AIMessage(content=ai_response)
    updated_messages = messages + [ai_message]

    return {
        **state,
        "messages": updated_messages,
        "test_cases": test_cases,
        "test_review_count": 0,
        "waiting_for_user_review": True,
        "test_requirement": requirement,
        "original_analysis": original_analysis,
        "used_multimodal": used_multimodal
    }


# 以下函数是旧版测试用例生成工作流的节点，已被 testcase_generation_bridge_node 替代
# 保留这些函数定义以保持向后兼容性

def generate_test_case_node(state: TestCaseGenerationState) -> TestCaseGenerationState:
    """
    节点1：根据需求生成测试用例（旧版，已被 testcase_generation_bridge_node 替代）
    """
    print("[警告] generate_test_case_node 已被 testcase_generation_bridge_node 替代")
    return state


def wait_for_user_review_node(state: TestCaseGenerationState) -> TestCaseGenerationState:
    """
    节点2：等待用户评审（旧版，已被 testcase_generation_bridge_node 替代）
    """
    print("[警告] wait_for_user_review_node 已被 testcase_generation_bridge_node 替代")
    return state


def save_test_case_to_excel_node(state: TestCaseGenerationState) -> TestCaseGenerationState:
    """
    节点3：保存测试用例到Excel（旧版，已被 testcase_generation_bridge_node 替代）
    """
    print("[警告] save_test_case_to_excel_node 已被 testcase_generation_bridge_node 替代")
    return state


def review_decision_edge(state: TestCaseGenerationState) -> str:
    """
    条件边：评审决策（旧版，已被 testcase_generation_bridge_node 替代）
    """
    print("[警告] review_decision_edge 已被 testcase_generation_bridge_node 替代")
    return "save_to_excel"

