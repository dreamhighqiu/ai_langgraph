"""
图表生成工具模块
负责生成测试结果可视化图表
"""
import re
import base64
from langchain_core.messages import HumanMessage
from file_rag.core.llm import create_llm
from .mcp_tools import get_chart_mcp_tools


async def generate_test_result_chart(test_execution_result: str, test_report: str) -> str:
    """
    根据测试执行结果生成图表

    Args:
        test_execution_result: 测试执行结果
        test_report: 测试报告

    Returns:
        图表的 HTML 代码，如果生成失败则返回空字符串
    """
    try:
        from langgraph.prebuilt import create_react_agent

        # 加载图表 MCP 工具
        chart_tools = await get_chart_mcp_tools()

        if not chart_tools:
            print("[图表] Chart MCP 工具不可用，跳过图表生成")
            return ""

        # 获取模型
        model = create_llm()

        # 创建图表生成 Agent
        chart_agent = create_react_agent(
            model,
            chart_tools
        )

        # 构建图表生成提示词
        chart_prompt = f"""请根据以下测试报告，生成一个测试结果统计图表。

测试报告：
{test_report}

请分析测试报告中的测试用例执行情况，统计：
1. 通过的测试用例数量
2. 失败的测试用例数量
3. 跳过的测试用例数量（如果有）

然后使用 create_chart 工具生成一个**柱状图**或**饼图**，展示测试结果统计。

图表要求：
- 标题：测试结果统计
- 数据：通过、失败、跳过的数量
- 颜色：通过用绿色，失败用红色，跳过用灰色
- 图表类型：柱状图（bar）或饼图（pie）

请调用 create_chart 工具生成图表。"""

        # 使用 Agent 生成图表
        print("[图表] 正在分析测试结果并生成图表...")
        agent_result = await chart_agent.ainvoke(
            {"messages": [HumanMessage(content=chart_prompt)]},
            config={"recursion_limit": 20}
        )

        # 提取图表结果
        all_messages = agent_result.get("messages", [])

        # 查找工具调用结果 - 寻找图片 URL
        chart_url = ""

        # 优先从 ToolMessage 中查找（工具返回的结果）
        for msg in all_messages:
            # 检查消息类型
            msg_type = type(msg).__name__
            if 'Tool' in msg_type and hasattr(msg, 'content') and msg.content:
                content = str(msg.content)
                # 只查找 alipayobjects.com 的 URL（AntV Chart MCP 返回的图片 URL）
                if 'alipayobjects.com' in content:
                    # 提取 URL - 更精确的正则表达式
                    url_pattern = r'https://[a-zA-Z0-9\-\.]+\.alipayobjects\.com/[^\s<>"{}|\\^`\[\]\)（）,，。；;]+?(?:\.png|\.jpg|\.jpeg|\.gif|\.svg|/original|/large)?'
                    urls = re.findall(url_pattern, content)
                    if urls:
                        chart_url = urls[0]
                        print(f"[图表] 从工具消息中找到图表 URL: {chart_url}")
                        break

        # 如果没有找到，尝试从所有消息中查找
        if not chart_url:
            for msg in all_messages:
                if hasattr(msg, 'content') and msg.content:
                    content = str(msg.content)
                    # 只查找 alipayobjects.com 的 URL
                    if 'alipayobjects.com' in content:
                        url_pattern = r'https://[a-zA-Z0-9\-\.]+\.alipayobjects\.com/[^\s<>"{}|\\^`\[\]\)（）,，。；;]+?(?:\.png|\.jpg|\.jpeg|\.gif|\.svg|/original|/large)?'
                        urls = re.findall(url_pattern, content)
                        if urls:
                            chart_url = urls[0]
                            print(f"[图表] 从消息中找到图表 URL: {chart_url}")
                            break

        if chart_url:
            # 尝试下载图片并转换为 base64
            try:
                import httpx
                print(f"[图表] 正在下载图片: {chart_url}")

                # 下载图片
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(chart_url)
                    if response.status_code == 200:
                        # 转换为 base64
                        image_base64 = base64.b64encode(response.content).decode('utf-8')

                        # 检测图片类型
                        content_type = response.headers.get('content-type', 'image/png')
                        if 'image/' in content_type:
                            image_format = content_type.split('/')[-1]
                        else:
                            # 从 URL 推断格式
                            if chart_url.endswith('.jpg') or chart_url.endswith('.jpeg'):
                                image_format = 'jpeg'
                            elif chart_url.endswith('.png'):
                                image_format = 'png'
                            elif chart_url.endswith('.gif'):
                                image_format = 'gif'
                            elif chart_url.endswith('.svg'):
                                image_format = 'svg+xml'
                            else:
                                image_format = 'png'  # 默认

                        # 创建 base64 图片 Markdown
                        chart_markdown = f"![测试结果统计图表](data:image/{image_format};base64,{image_base64})"
                        print("[图表] ✓ 图表下载并转换为 base64 成功")
                        return chart_markdown
                    else:
                        print(f"[图表] ⚠️ 下载图片失败，状态码: {response.status_code}")
                        # 降级：返回原始 URL
                        chart_markdown = f"![测试结果统计图表]({chart_url})\n\n*如果图片无法显示，请直接访问：[{chart_url}]({chart_url})*"
                        return chart_markdown
            except Exception as e:
                print(f"[图表] ⚠️ 下载图片时出错: {e}")
                # 降级：返回原始 URL
                chart_markdown = f"![测试结果统计图表]({chart_url})\n\n*如果图片无法显示，请直接访问：[{chart_url}]({chart_url})*"
                return chart_markdown
        else:
            print("[图表] ⚠️ 未能提取图表 URL")
            # 打印所有消息内容用于调试
            print("[图表] [调试] 所有消息内容:")
            for i, msg in enumerate(all_messages):
                print(f"[图表] [调试] 消息 {i}: 类型={type(msg).__name__}, 内容={str(msg.content)[:200]}")
            return ""

    except Exception as e:
        print(f"[图表] ⚠️ 生成图表时出错: {e}")
        import traceback
        traceback.print_exc()
        return ""

