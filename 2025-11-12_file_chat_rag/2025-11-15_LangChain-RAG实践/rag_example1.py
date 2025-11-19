from langchain_pymupdf4llm import PyMuPDF4LLMLoader

loader = PyMuPDF4LLMLoader(
    "../llm_course.pdf",
                mode="single",  # 作为单个文档处理  page
                table_strategy="lines"  # 提取表格
            )
documents = loader.load()

from langchain_text_splitters import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = text_splitter.split_text(documents[0].page_content)
print(len(texts))
print(texts)