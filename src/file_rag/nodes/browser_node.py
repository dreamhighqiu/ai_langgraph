"""
浏览器操作节点模块
负责使用 DeepSeek + MCP Chrome 工具执行浏览器操作
"""
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from file_rag.models import ConversationState
from file_rag.core.llm import create_llm
from file_rag.utils.mcp_tools import get_all_mcp_tools


async def browser_operation_node(state: ConversationState) -> ConversationState:
    """
    浏览器操作节点：使用 DeepSeek + MCP Chrome 工具执行浏览器操作

    与自动化测试节点的区别：
    - 自动化测试：生成详细的测试报告
    - 浏览器操作：只执行操作并返回结果，不生成测试报告

    工作流程：
    1. 使用 DeepSeek 分析用户需求
    2. 使用 ReAct Agent + MCP Chrome 工具执行操作
    3. 返回执行结果

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态，包含操作结果
    """
    print("\n=== 节点6：浏览器操作节点 ===")
    print("开始执行浏览器操作任务...")

    messages = state.get("messages", [])

    # 提取用户的操作需求
    user_request = ""
    for msg in messages:
        if isinstance(msg, dict):
            content = msg.get('content', '')
            if isinstance(content, str):
                user_request = content
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text':
                        user_request = item.get('text', '')
        elif isinstance(msg, HumanMessage):
            if isinstance(msg.content, str):
                user_request = msg.content

    print(f"[操作任务] 用户需求: {user_request}")

    # 步骤1: 检查 MCP 工具是否可用 - 异步加载
    print("\n[步骤1] 检查 MCP Chrome 工具...")
    mcp_tools = await get_all_mcp_tools()

    if not mcp_tools:
        # MCP 工具不可用，返回错误信息
        print("[错误] MCP Chrome 工具不可用，无法执行浏览器操作")

        error_message = f"""⚠️ 无法执行浏览器操作

由于 MCP Chrome 工具当前不可用，无法执行您请求的操作。

**如何启用 Chrome 工具：**
1. 确保 Chrome MCP 服务正在运行（http://127.0.0.1:12306/mcp）
2. 确保 langchain-mcp-adapters 已安装
3. 在 mcp_config.py 中启用了 chrome_mcp

然后重新提交请求。"""

        response = AIMessage(content=error_message)
        updated_messages = messages + [response]

        return {
            **state,
            "messages": updated_messages,
            "extracted_content": ""
        }

    # 步骤2: 使用 ReAct Agent + MCP 工具执行操作
    print(f"\n[步骤2] 创建 ReAct Agent 并执行操作（共 {len(mcp_tools)} 个工具可用）...")

    # 获取模型
    model = create_llm()

    # 创建 ReAct Agent
    operation_agent = create_react_agent(
        model,
        mcp_tools
    )

    # 构建执行提示词
    execution_prompt = f"""你是一个浏览器操作助手。请使用提供的 Chrome 工具执行以下操作：

{user_request}

**请按照用户的要求执行操作，并返回操作结果。**

可用的工具包括：
- chrome_navigate: 打开网页
- chrome_get_web_content: 获取网页内容
- chrome_click_element: 点击元素
- chrome_fill_or_select: 填写表单
- chrome_get_interactive_elements: 获取可交互元素
- chrome_screenshot: 截图
- 等等...

**重要：必须实际调用工具执行操作，不要只描述步骤！现在开始执行！**"""

    try:
        # 使用 ReAct Agent 执行操作
        print("[执行] 启动 ReAct Agent 执行操作...")
        print("[执行] Agent 将自动调用 Chrome 工具...")

        # 使用 ainvoke 异步调用
        agent_result = await operation_agent.ainvoke(
            {"messages": [HumanMessage(content=execution_prompt)]},
            config={"recursion_limit": 50}
        )

        # 提取所有消息
        all_messages = agent_result.get("messages", [])

        # 打印工具调用情况
        tool_calls_count = 0
        for msg in all_messages:
            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                tool_calls_count += len(msg.tool_calls)
                for tool_call in msg.tool_calls:
                    print(f"[工具调用] {tool_call.get('name', 'unknown')}")

        print(f"[执行] 总共调用了 {tool_calls_count} 次工具")

        # 提取最终结果
        operation_result = ""
        for msg in reversed(all_messages):
            if isinstance(msg, AIMessage) and msg.content:
                operation_result = msg.content
                break

        if not operation_result:
            operation_result = "操作执行完成，但未获取到结果"

        print(f"[执行结果] {operation_result[:300]}...")

    except Exception as e:
        import traceback
        print(f"[错误] 操作执行失败: {e}")
        traceback.print_exc()
        operation_result = f"操作执行过程中出现错误: {str(e)}\n\n详细错误信息请查看日志。"

    # 返回结果
    response = AIMessage(content=operation_result)
    updated_messages = messages + [response]

    return {
        **state,
        "messages": updated_messages,
        "extracted_content": operation_result
    }

