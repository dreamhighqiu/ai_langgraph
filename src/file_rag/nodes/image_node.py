"""
图片处理节点模块
负责使用豆包多模态模型处理图片对话
"""
from file_rag.models import ConversationState
from file_rag.core.llm import create_chat_llm


def image_processing_node(state: ConversationState) -> ConversationState:
    """
    图片处理节点：使用豆包多模态模型处理图片对话

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态，包含AI回复
    """
    print("\n=== 节点2：图片处理节点 ===")
    print("使用豆包多模态模型处理图片...")

    messages = state.get("messages", [])

    # 过滤消息：只保留 human 和 ai 类型的消息
    # 移除 tool 类型的消息，因为豆包 API 可能不支持
    filtered_messages = []
    for msg in messages:
        # 处理 LangChain 消息对象
        if hasattr(msg, 'type'):
            if msg.type in ['human', 'ai', 'system']:
                filtered_messages.append(msg)
        # 处理字典格式的消息
        elif isinstance(msg, dict):
            msg_type = msg.get('type', '')
            if msg_type in ['human', 'ai', 'system']:
                filtered_messages.append(msg)

    print(f"[DEBUG] 原始消息数: {len(messages)}, 过滤后消息数: {len(filtered_messages)}")

    # 使用豆包多模态模型
    model = create_chat_llm()
    response = model.invoke(filtered_messages)

    print(f"豆包模型回复: {response.content[:100]}...")

    # 将AI回复添加到消息历史
    updated_messages = messages + [response]

    return {
        **state,
        "messages": updated_messages
    }

