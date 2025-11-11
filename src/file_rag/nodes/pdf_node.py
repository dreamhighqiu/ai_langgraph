"""
PDF处理节点模块
负责提取PDF内容（文本+图片）并使用多模态模型处理
"""
from langchain_core.messages import HumanMessage
from file_rag.models import ConversationState
from file_rag.core.llm import create_llm,create_chat_llm
from file_rag.utils.pdf_utils import extract_pdf_content, extract_pdf_images


def pdf_processing_node(state: ConversationState) -> ConversationState:
    """
    PDF处理节点：提取PDF内容（文本+图片）并使用多模态模型处理

    处理步骤：
    1. 从消息中提取base64编码的PDF数据
    2. 提取PDF文本内容
    3. 提取PDF中的图片
    4. 如果有图片，使用豆包多模态模型识别图片内容
    5. 将文本、图片识别结果和用户问题一起发送给DeepSeek

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态，包含提取的内容和AI回复
    """
    print("\n=== 节点3：PDF处理节点（支持图片识别）===")

    messages = state.get("messages", [])
    last_message = messages[-1] if messages else None

    # 提取PDF数据和用户问题
    user_question = ""
    pdf_base64_data = ""
    pdf_filename = ""

    # 处理 dict 格式的消息（LangGraph Server）
    if isinstance(last_message, dict):
        content = last_message.get('content', [])
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict):
                    if item.get('type') == 'text':
                        user_question = item.get('text', '')
                    elif item.get('type') == 'file' and 'pdf' in item.get('mime_type', '').lower():
                        pdf_base64_data = item.get('data', '')
                        pdf_filename = item.get('metadata', {}).get('filename', 'unknown.pdf')
    # 处理 HumanMessage 格式
    elif isinstance(last_message, HumanMessage) and isinstance(last_message.content, list):
        for item in last_message.content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    user_question = item.get('text', '')
                elif item.get('type') == 'file' and 'pdf' in item.get('mime_type', '').lower():
                    pdf_base64_data = item.get('data', '')
                    pdf_filename = item.get('metadata', {}).get('filename', 'unknown.pdf')

    print(f"用户问题: {user_question}")
    print(f"PDF文件名: {pdf_filename}")
    print(f"[DEBUG] PDF数据长度: {len(pdf_base64_data)} 字符")

    # 提取PDF文本内容
    if pdf_base64_data:
        print("\n[步骤1] 正在提取PDF文本内容...")
        extracted_text = extract_pdf_content(pdf_base64_data)
        print(f"提取的文本长度: {len(extracted_text)} 字符")
        print(f"文本预览: {extracted_text[:200]}...")

        # 提取PDF图片
        print("\n[步骤2] 正在提取PDF图片...")
        extracted_images = extract_pdf_images(pdf_base64_data)
        print(f"提取了 {len(extracted_images)} 张图片")

        # 如果有图片，使用豆包模型识别
        image_descriptions = []
        if extracted_images:
            print("\n[步骤3] 使用GPT-5 多模态模型识别图片...")
            doubao_model = create_chat_llm()

            for idx, img_info in enumerate(extracted_images):
                print(f"  识别第 {idx + 1}/{len(extracted_images)} 张图片（第{img_info['page']}页）...")

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

        # 组合所有内容
        combined_content = f"""PDF文件名: {pdf_filename}

【文本内容】
{extracted_text}
"""

        if image_descriptions:
            combined_content += "\n【图片内容】\n"
            for img_desc in image_descriptions:
                combined_content += f"\n图片 {img_desc['index']}（第{img_desc['page']}页）：\n{img_desc['description']}\n"

        extracted_content = combined_content

    else:
        extracted_content = "未找到PDF数据"
        print("警告: 未找到PDF数据")

    # 构建发送给DeepSeek的消息
    combined_message = f"""基于以下PDF文档内容回答问题。

{extracted_content}

用户问题: {user_question}

请根据PDF的文本内容和图片内容综合回答用户的问题。"""

    # 创建新的消息发送给DeepSeek
    deepseek_messages = [HumanMessage(content=combined_message)]

    print("\n[步骤4] 正在调用DeepSeek模型生成最终回答...")
    model = create_llm()
    response = model.invoke(deepseek_messages)

    print(f"DeepSeek回复: {response.content[:100]}...")

    # 将AI回复添加到原始消息历史
    updated_messages = messages + [response]

    return {
        **state,
        "messages": updated_messages,
        "extracted_content": extracted_content
    }

