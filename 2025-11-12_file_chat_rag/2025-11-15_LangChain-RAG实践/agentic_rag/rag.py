from langchain.agents import create_agent
from langchain_deepseek import ChatDeepSeek
from langchain_milvus import Milvus
from langchain_ollama import OllamaEmbeddings

URI = "http://207.246.94.177:19530"
embeddings = OllamaEmbeddings(
    model="qwen3-embedding:0.6b",
    base_url="http://207.246.94.177:11434"
)
vector_store_1 = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": URI},
    index_params={"index_type": "FLAT", "metric_type": "L2"},
    collection_name="langchainweb",
)
vector_store_2 = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": URI},
    index_params={"index_type": "FLAT", "metric_type": "L2"},
    collection_name="LangChainCollection",
)
retriever_1 = vector_store_1.as_retriever()
retriever_2 = vector_store_2.as_retriever()

from langchain_classic.tools.retriever import create_retriever_tool

retriever_tool_1 = create_retriever_tool(
    retriever_1,
    "retrieve_docs",
    "检索与大模型及智能体相关的文档",
)
retriever_tool_2 = create_retriever_tool(
    retriever_2,
    "retrieve_course",
    "检索与课程相关的文档",
)
model = ChatDeepSeek(
            api_key="sk-23b59f8b672f4d319cf7d92c8e7a7257",
            model="deepseek-chat",
        )
agent = create_agent(
    model=model,
    tools=[retriever_tool_1, retriever_tool_2],
    system_prompt="你擅长基于用户提供的上下文信息回答用户问题。如果上下文中没有相关的信息，请回答“抱歉，没有找到相关的信息。”",
    name="chat_agent",
)
