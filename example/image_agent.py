"""
文件 RAG 调试脚本
用于测试 Agent 中间件功能
可以被 LangGraph API 加载
"""

import logging
from typing import Optional

from langchain.agents import create_agent, AgentState
from langchain.agents.middleware import before_model
from langchain_core.runnables import RunnableConfig

from llm import create_llm

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建 LLM 实例
llm_gpt= create_llm(
    model="gpt-4o",
)

@before_model
def add_messages_middleware(state: AgentState, runtime) -> None:
    """
    在模型调用前的中间件

    参数:
        state: Agent 状态
        runtime: 运行时对象
    """
    logger.info("中间件执行: 模型调用前")
    logger.info(f"当前消息数: {len(state.get('messages', []))}")
    print("state:", state["messages"])
    return None


def create_agent_graph(config: Optional[RunnableConfig] = None):
    """
    创建 Agent 图工厂函数

    这个函数被 LangGraph API 调用来创建图实例

    参数:
        config: LangGraph API 配置对象(可选)

    返回:
        CompiledGraph: 编译后的 Agent 图
    """
    agent = create_agent(
        model=create_llm(),
        tools=[],
        middleware=[add_messages_middleware],
    )
    return agent

agent_image = create_agent(
        model=llm_gpt,
        tools=[],
        middleware=[add_messages_middleware],
    )
    
# 测试 Agent
if __name__ == "__main__":
    logger.info("开始测试 Agent 中间件...")

    agent = create_agent_graph()
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Hello world"}]
    })

    logger.info("Agent 响应完成")