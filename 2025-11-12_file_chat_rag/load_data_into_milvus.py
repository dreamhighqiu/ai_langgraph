from langchain_milvus import Milvus, BM25BuiltInFunction

from langchain_ollama import OllamaEmbeddings

import bs4
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import create_retriever_tool
from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
# 加载文档
loader = WebBaseLoader(
    web_paths=(
        "https://lilianweng.github.io/posts/2023-06-23-agent/",
        "https://lilianweng.github.io/posts/2023-03-15-prompt-engineering/",
    ),
    bs_kwargs=dict(
        parse_only=bs4.SoupStrainer(
            class_=("post-content", "post-title", "post-header")
        )
    ),
)
# from langchain_pymupdf4llm import PyMuPDF4LLMLoader
# pdf_path = "llm_course.pdf"
# loader = PyMuPDF4LLMLoader(
#     pdf_path,
#     mode="single",  # 作为单个文档处理
#     # extract_images=True,  # 提取图片
#     table_strategy="lines",  # 提取表格
#     # images_parser=llm_parser,
# )
documents = loader.load()

# 分块
text_splitter = RecursiveCharacterTextSplitter(chunk_size=2048, chunk_overlap=200)
docs = text_splitter.split_documents(documents)

uri = "http://54.179.103.192:19530"

#嵌入向量数据库
embeddings = OllamaEmbeddings(model="qwen3-embedding:0.6b", base_url="http://54.179.103.192:11434")
vectorstore = Milvus.from_documents(
    documents=docs,
    embedding=embeddings,
    builtin_function=BM25BuiltInFunction(),
    # `dense` is for OpenAI embeddings, `sparse` is the output field of BM25 function
    vector_field=["dense", "sparse"],
    connection_args={
        "uri": uri,
    },
    consistency_level="Strong",
    collection_name="course_collection",
    drop_old=True,
)
# vector_store = Milvus(
#     embedding_function=embeddings,
#     connection_args={"uri": "http://35.235.113.151:19530"},
#     builtin_function=BM25BuiltInFunction(),
# )


# # 从向量数据库获取内容
vector_store1 = Milvus(
    embedding_function=embeddings,
    connection_args={"uri": uri},
    index_params={"index_type": "FLAT", "metric_type": "L2"},
    collection_name="course_collection",
)
results = vector_store1.similarity_search_with_score("介绍一下LangGraph")
# print(results)
doc, score = results[0]
print(f"Score: {score}\n")
print(doc)
