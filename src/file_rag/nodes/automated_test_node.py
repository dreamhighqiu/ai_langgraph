"""
自动化测试节点模块
负责使用 DeepSeek + MCP Chrome 工具执行自动化测试
"""
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.prebuilt import create_react_agent
from file_rag.models import ConversationState
from file_rag.core.llm import create_llm
from file_rag.utils.mcp_tools import get_all_mcp_tools
from file_rag.utils.chart_utils import generate_test_result_chart
from file_rag.utils.html_report_generator import HTMLReportGenerator

# 导入性能配置
try:
    from file_rag.performance_config import CURRENT_CONFIG
except ImportError:
    # 如果没有性能配置文件，使用默认配置
    CURRENT_CONFIG = {
        "enable_chart_by_default": False,
        "recursion_limit": 30,
        "fast_mode": True,
        "verbose": True,
        "generate_detailed_report": True,
    }


async def automated_test_node(state: ConversationState) -> ConversationState:
    """
    自动化测试节点：使用 DeepSeek + MCP Chrome 工具执行自动化测试

    工作流程：
    1. 使用 DeepSeek 分析用户需求，生成测试计划
    2. 使用 ReAct Agent + MCP Chrome 工具真正执行测试
    3. 收集测试结果
    4. 生成详细测试报告

    Args:
        state: 当前对话状态

    Returns:
        更新后的状态，包含测试报告
    """
    print("\n=== 节点5：自动化测试节点 ===")
    print("开始执行自动化测试任务...")

    messages = state.get("messages", [])

    # 提取用户的测试需求
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

    print(f"[测试任务] 用户需求: {user_request}")

    # 步骤1: 检查 MCP 工具是否可用 - 异步加载
    print("\n[步骤1] 检查 MCP Chrome 工具...")
    mcp_tools = await get_all_mcp_tools()

    if not mcp_tools:
        # MCP 工具不可用，返回错误信息
        print("[错误] MCP Chrome 工具不可用，无法执行自动化测试")

        report = f"""# 自动化测试报告

## ⚠️ 测试状态：未执行

由于 MCP Chrome 工具当前不可用，无法执行自动化测试。

## 💡 如何执行测试

要执行自动化测试，请确保：
1. Chrome MCP 服务正在运行（http://127.0.0.1:12306/mcp）
2. langchain-mcp-adapters 已安装
3. 在 mcp_config.py 中启用了 chrome_mcp

然后重新提交测试请求。
"""

        response = AIMessage(content=report)
        updated_messages = messages + [response]

        return {
            **state,
            "messages": updated_messages,
            "extracted_content": ""
        }

    # 步骤2: 使用 ReAct Agent + MCP 工具直接执行测试
    print(f"\n[步骤2] 创建 ReAct Agent 并执行测试（共 {len(mcp_tools)} 个工具可用）...")

    # 获取模型
    model = create_llm()

    # 创建 ReAct Agent - 使用 prompt 参数
    test_agent = create_react_agent(
        model,
        mcp_tools
    )

    # 构建执行提示词 - 明确要求使用工具（恢复原始详细版本）
    execution_prompt = f"""你是一个自动化测试执行器。请使用提供的 Chrome 工具执行以下测试任务：

{user_request}

**必须使用工具执行以下步骤：**

测试用例1：成功登录测试
1. 使用 chrome_navigate 打开 https://www.saucedemo.com/
2. 使用 chrome_get_interactive_elements 查找登录表单元素
3. 使用 chrome_fill_or_select 填写用户名 "standard_user"
4. 使用 chrome_fill_or_select 填写密码 "secret_sauce"
5. 使用 chrome_click_element 点击登录按钮
6. 使用 chrome_get_web_content 验证登录成功

测试用例2：错误密码登录测试
1. 使用 chrome_navigate 刷新页面
2. 使用 chrome_fill_or_select 填写用户名 "standard_user"
3. 使用 chrome_fill_or_select 填写错误密码 "wrong_password"
4. 使用 chrome_click_element 点击登录按钮
5. 使用 chrome_get_web_content 验证错误提示

测试用例3：空用户名登录测试
1. 使用 chrome_navigate 刷新页面
2. 使用 chrome_fill_or_select 只填写密码 "secret_sauce"
3. 使用 chrome_click_element 点击登录按钮
4. 使用 chrome_get_web_content 验证错误提示

**重要：必须实际调用工具，不要只描述步骤！现在开始执行！**"""

    try:
        # 使用 ReAct Agent 执行测试 - 使用异步调用
        print("[执行] 启动 ReAct Agent 执行测试...")
        print("[执行] Agent 将自动调用 Chrome 工具...")
        print("[提示] 为提高速度，已优化执行流程...")

        # 使用 ainvoke 异步调用，因为 MCP 工具是异步的
        # 使用原始的递归限制 50（足够执行 3 个测试用例）
        recursion_limit = 50
        print(f"[配置] 递归限制: {recursion_limit}")

        # 添加超时机制
        import asyncio
        try:
            agent_result = await asyncio.wait_for(
                test_agent.ainvoke(
                    {"messages": [HumanMessage(content=execution_prompt)]},
                    config={"recursion_limit": recursion_limit}
                ),
                timeout=180.0  # 3分钟超时
            )
        except asyncio.TimeoutError:
            print("[错误] Agent 执行超时（3分钟）")
            raise Exception("测试执行超时，请检查网络连接或减少测试用例数量")
        except Exception as e:
            # 捕获递归限制错误
            if "Recursion limit" in str(e):
                print(f"[错误] 达到递归限制 {recursion_limit}，测试可能未完全执行")
                # 继续处理，尝试从已有的消息中提取结果
                agent_result = {"messages": []}
            else:
                raise

        # 提取所有消息，包括工具调用
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
        test_execution_result = ""
        for msg in reversed(all_messages):
            if isinstance(msg, AIMessage) and msg.content:
                test_execution_result = msg.content
                break

        if not test_execution_result:
            test_execution_result = "测试执行完成，但未获取到结果"

        print(f"[执行结果] {test_execution_result[:300]}...")

    except Exception as e:
        import traceback
        print(f"[错误] 测试执行失败: {e}")
        traceback.print_exc()
        test_execution_result = f"测试执行过程中出现错误: {str(e)}\n\n详细错误信息请查看日志。"

    # 步骤3: 生成详细测试报告
    print("\n[步骤3] 生成详细测试报告...")

    report_prompt = f"""请根据以下测试执行结果，生成一份详细的测试报告：

## 用户需求
{user_request}

## 执行结果
{test_execution_result}

请生成一份专业的测试报告，包括：
1. **测试概述**: 测试的目标和范围
2. **测试环境**: 测试网站和工具
3. **测试用例**: 列出所有测试用例
4. **测试执行详情**: 每个测试用例的执行步骤和结果
5. **测试结果统计**: 通过/失败的统计
6. **问题总结**: 发现的问题（如果有）
7. **结论和建议**: 测试结论和改进建议

请使用 Markdown 格式，让报告清晰易读。"""

    report_response = model.invoke([HumanMessage(content=report_prompt)])
    final_report = report_response.content

    print(f"[测试报告] 已生成")
    print(f"{final_report[:300]}...")

    # 步骤4: 生成测试结果图表（可选 - 默认跳过以提高速度）
    # 优先使用状态中的配置，其次使用性能配置
    enable_chart = state.get("enable_chart", CURRENT_CONFIG.get("enable_chart_by_default", False))

    if enable_chart:
        print("\n[步骤4] 生成测试结果图表...")
        chart_html = await generate_test_result_chart(test_execution_result, final_report)

        # 如果成功生成图表，将图表添加到报告中
        if chart_html:
            final_report_with_chart = f"""{final_report}

---

## 📊 测试结果可视化

{chart_html}

---

*图表由 AntV Chart MCP 服务生成*
"""
            print(f"[图表] 已生成测试结果图表")
        else:
            final_report_with_chart = final_report
            print(f"[图表] 未生成图表（Chart MCP 服务可能未启用）")
    else:
        final_report_with_chart = final_report
        print(f"[步骤4] 跳过图表生成（为提高速度，默认关闭。如需图表，请在状态中设置 enable_chart=True）")

    # 步骤5: 生成HTML测试报告
    print("\n[步骤5] 生成HTML测试报告...")
    try:
        html_report_path = HTMLReportGenerator.generate_html_report(final_report_with_chart)
        print(f"[HTML报告] ✓ HTML测试报告已生成")
        print(f"[HTML报告] 📁 报告路径: {html_report_path}")

        # 在最终报告中添加HTML报告路径信息
        final_report_with_html_info = f"""{final_report_with_chart}

---

## 📄 HTML测试报告

HTML格式的测试报告已生成，可以在浏览器中查看更美观的报告。

**报告路径**: `{html_report_path}`

您可以直接在浏览器中打开此文件查看详细的测试报告。
"""
    except Exception as e:
        print(f"[HTML报告] ⚠️ 生成HTML报告时出错: {e}")
        import traceback
        traceback.print_exc()
        # 如果生成失败，不影响主流程，继续使用原报告
        final_report_with_html_info = final_report_with_chart

    # 返回结果
    response = AIMessage(content=final_report_with_html_info)
    updated_messages = messages + [response]

    return {
        **state,
        "messages": updated_messages,
        "extracted_content": test_execution_result
    }

