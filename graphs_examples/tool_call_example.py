"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import os
from typing import TypedDict, Annotated

from langchain.tools import tool
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langgraph.constants import START, END
from langgraph.graph import MessagesState, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

os.environ["DEEPSEEK_API_KEY"] = "sk-7443d4458d1444d2ac620964e4f58767"

model = init_chat_model(
    "deepseek:deepseek-chat",
    temperature=0
)


# Define tools
@tool
def multiply(a: int, b: int) -> int:
    """Multiply `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a * b


@tool
def add(a: int, b: int) -> int:
    """Adds `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a + b


@tool
def divide(a: int, b: int) -> float:
    """Divide `a` and `b`.

    Args:
        a: First int
        b: Second int
    """
    return a / b


# Augment the LLM with tools
tools = [add, multiply, divide]

# 将工具绑定到大模型对象

# 结果：应该调用哪个工具，以及工具参数是什么？

# 执行工具


# -------------------------------------
# 定义传输数据的状态

# class State(TypedDict):
#     messages: Annotated[list[AnyMessage], add_messages]

def call_llm_node(state: MessagesState):
    """Write a story"""
    model_with_tools = model.bind_tools(tools)
    # 将大模型绑定的工具进行及用户问题一起发送给大模型，由大模型觉得调用哪些工具，同时生成工具的参数
    result = model_with_tools.invoke(state["messages"])
    return {"messages": result}

def call_llm_node_2(state: MessagesState):
    """Write a joke"""
    result = model.invoke(state["messages"])
    return {"messages": result}

def condition_edge(state: MessagesState):
    """Decide if we should continue the loop or stop based upon whether the LLM made a tool call"""
    a = 10
    if a>10:
        return "tool_node"
    else:
        return "call_llm_node_2"


tool_node = ToolNode(tools)

# Build workflow
agent_builder = StateGraph(MessagesState)

# 添加节点
agent_builder.add_node("llm_call", call_llm_node)
agent_builder.add_node("tool_node", tool_node)
agent_builder.add_node("call_llm_node_2", call_llm_node_2)

# Add edges to connect nodes
agent_builder.add_edge(START, "llm_call")
agent_builder.add_conditional_edges("llm_call", "condition_edge")
# agent_builder.add_edge("llm_call", "tool_node")
# agent_builder.add_edge("tool_node", "call_llm_node_2")

# Compile the agent
graph = agent_builder.compile()

#
# # Invoke
# from langchain.messages import HumanMessage
# messages = [HumanMessage(content="Add 3 and 4.")]
# messages = agent.invoke({"messages": messages})
# for m in messages["messages"]:
#     m.pretty_print()