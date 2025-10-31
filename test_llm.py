from llm import create_llm, create_gpt5_llm, LLMConfig
from langchain_core.messages import HumanMessage

# 创建 LLM
# llm = create_llm()

# 调用
# response = llm.invoke("你是什么大模型")
# print(response)

# for message in llm.stream('测试用例怎么设计 更专业'):
#     print(message,flush=True)


# from langgraph.graph import StateGraph, END
# from llm import create_llm
#
# def chat_node(state):
#     llm = create_llm()  # 一行代码!
#     response = llm.invoke(state["messages"])
#     return {"messages": [response]}
#
# workflow = StateGraph(dict)
# workflow.add_node("chat", chat_node)
# workflow.set_entry_point("chat")
# workflow.add_edge("chat", END)
# app = workflow.compile()


llm = create_llm(model="gpt-5")
resp = llm.invoke("你是什么模型")
print(resp)