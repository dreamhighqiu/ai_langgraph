"""
Java Playwright UI 测试自动化 Agent

此包提供基于 Java + Playwright 的 UI 自动化测试能力。

主要组件：
- agent.py: Agent 主文件，驱动 Skills 工作
- agent_skills/: Skills 定义目录
  - planner/: 测试规划器
  - generator/: Java 代码生成器
  - healer/: 测试修复器
- workspace/: Agent 工作区，存放生成的文件

使用方法：
    from agents.ui_java.agent import agent
    
    # agent 是一个异步上下文管理器
    async with agent() as ui_java_agent:
        # 使用 agent 生成 Java 测试代码
        result = await ui_java_agent.ainvoke({
            "messages": [{"role": "user", "content": "创建设备库存页面的测试计划"}]
        })
"""

__version__ = "1.0.0"
__author__ = "Test Automation Team"

