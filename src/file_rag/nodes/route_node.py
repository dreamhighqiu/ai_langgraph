"""
路由节点模块
负责检测用户消息类型并决定路由目标
"""
import json
from file_rag.models import ConversationState
from file_rag.utils.detection import detect_file_type


def route_node(state: ConversationState) -> ConversationState:
    """
    路由节点：检测用户上传的文件类型

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态，包含文件类型信息
    """
    print("\n=== 节点1：路由节点 - 检测文件类型 ===")

    messages = state.get("messages", [])

    # 检查是否正在等待用户评审
    waiting_for_review = state.get("waiting_for_user_review", False)
    test_cases = state.get("test_cases", "")

    print(f"[状态检查] 等待评审: {waiting_for_review}, 已有测试用例: {bool(test_cases)}")

    # 打印完整的消息内容（用于调试）
    print(f"[DEBUG] 完整消息内容:")
    for idx, msg in enumerate(messages):
        if isinstance(msg, dict):
            # 只打印前1000个字符，避免日志过长
            msg_str = json.dumps(msg, ensure_ascii=False)
            print(f"  消息 {idx}: {type(msg).__name__}")
            if len(msg_str) > 1000:
                print(f"  消息{idx}: {msg_str[:1000]}... (总长度: {len(msg_str)})")
            else:
                print(f"  消息{idx}: {msg_str}")
        else:
            print(f"  消息{idx}: {type(msg).__name__}")

    # 如果正在等待用户评审，检查用户输入是否是评审反馈还是新任务
    if waiting_for_review and test_cases:
        # 提取最后一条用户消息
        last_user_input = ""
        for msg in reversed(messages):
            if isinstance(msg, dict) and msg.get("type") == "human":
                content = msg.get("content", "")
                if isinstance(content, str):
                    last_user_input = content
                    break
                elif isinstance(content, list):
                    for item in content:
                        if isinstance(item, dict) and item.get("type") == "text":
                            last_user_input = item.get("text", "")
                            break
                if last_user_input:
                    break
            elif hasattr(msg, 'type') and msg.type == "human":
                if isinstance(msg.content, str):
                    last_user_input = msg.content
                    break

        # 判断是否是评审反馈（简短的"通过"或"不通过"反馈）
        # 如果包含明确的新任务关键词（如"打开"、"执行"、"访问"等），则认为是新任务
        new_task_keywords = ['打开', '访问', '执行', '登录', '测试报告', '自动化', 'http://', 'https://', 'www.']
        is_new_task = any(keyword in last_user_input for keyword in new_task_keywords)

        if is_new_task:
            print(f"[DEBUG] 🎯 检测到新任务请求（非评审反馈），清除评审状态并重新路由")
            # 清除评审状态
            state = {
                **state,
                "waiting_for_user_review": False,
                "test_cases": "",
                "test_review_count": 0
            }
            # 重新检测文件类型
            file_type = detect_file_type(messages)
        else:
            print(f"[DEBUG] 🎯 检测到正在等待用户评审 → 路由到 testcase_generation")
            file_type = "testcase_generation"
    else:
        file_type = detect_file_type(messages)

    print(f"检测到的文件类型: {file_type}")

    return {
        **state,
        "file_type": file_type
    }

