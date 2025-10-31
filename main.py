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
        # excel_mcp_tools() +
        filesystem_mcp_tools()+
        time_mcp_tools()
        # markdown_mcp_tools()
    ),
    system_prompt="你是一个有用的助手，可以进行浏览器自动化操作、处理文件和生成图表。"
)

# Chrome Agent - 使用 Chrome 浏览器控制工具
chrome_agent = create_agent(
    model=llm,
    tools=chrome_mcp_local_tools(),
    system_prompt="你是一个有用的助手，可以控制 Chrome 浏览器。"
)

print("✓ 所有 Agent 创建成功")