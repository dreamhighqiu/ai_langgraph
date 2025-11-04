"""
LangGraph Agent 主文件
"""

from llm import create_llm
from tools import (
    get_weather,
    get_tavily_search_mcp_tools,
    chrome_mcp_local_tools,
    chart_mcp_tools,
    # markdown_mcp_tools,
    # excel_mcp_tools,
    filesystem_mcp_tools,
    time_mcp_tools,
    EdgeOne_mcp_tools,
    get_test_case_generator_tools
)
from langchain.agents import create_agent

# 创建 LLM 实例
llm = create_llm()

# 创建基础 Agent (使用简单工具)
agent = create_agent(
    model=llm,
    tools=[get_weather],
    system_prompt="你是一个有用的助手，可以查询天气信息。"
)

# Web Agent - 使用搜索和图表工具
web_agent = create_agent(
    model=llm,
    tools=get_tavily_search_mcp_tools() + chart_mcp_tools(),
    system_prompt="你是一个有用的助手，可以进行网络搜索并生成图表。"
)

# Playwright Agent - 使用浏览器自动化和文件处理工具
# https://github.com/hangwin/mcp-chrome/blob/master/README_zh.md
# 打开网页：http://playturbo-test2.mintegral.com/#/login  输入用户名 yunxia.qiu  密码 Qazwsx123 登录页面
playwright_agent = create_agent(
    model=llm,
    tools=(
        chrome_mcp_local_tools() +
        chart_mcp_tools() +
        filesystem_mcp_tools()+
        time_mcp_tools()+
        EdgeOne_mcp_tools()
    ),
    system_prompt="你是一个有用的助手，可以进行浏览器自动化操作、处理文件和生成图表。"
)

# Chrome Agent - 使用 Chrome 浏览器控制工具
chrome_agent = create_agent(
    model=llm,
    tools=chrome_mcp_local_tools(),
    system_prompt="你是一个有用的助手，可以控制 Chrome 浏览器。"
)

# 测试用例生成 Agent - 使用 Excel、文件系统和图表 MCP 工具
test_case_generator_agent = create_agent(
    model=llm,
    tools=get_test_case_generator_tools(),
    system_prompt="""你是一个专业的测试用例生成和管理助手。

你可以使用以下能力：
1. 生成高质量的测试用例
2. 评审测试用例质量
3. 使用 Excel 工具创建和编辑 Excel 文件
4. 使用文件系统工具保存和管理文件
5. 使用图表工具绘制测试用例统计图表

请确保生成的测试用例完整、清晰、可执行，并生成相应的统计图表。"""
)

print("✓ 所有 Agent 创建成功")
print("  - 基础 Agent (天气查询)")
print("  - Web Agent (搜索和图表)")
print("  - Playwright Agent (浏览器自动化)")
print("  - Chrome Agent (Chrome 控制)")
print("  - 测试用例生成 Agent (Excel 和文件系统)")