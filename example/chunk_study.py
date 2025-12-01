

from langchain_pymupdf4llm import PyMuPDF4LLMLoader
# pylint: disable  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Ym5GS1RBPT06ZWYzNjQ4MmM=

loader = PyMuPDF4LLMLoader(
    "pdf_text.pdf",
                mode="single",  # 作为单个文档处理
                table_strategy="lines"  # 提取表格
            )
documents = loader.load()

from langchain_text_splitters import RecursiveCharacterTextSplitter
# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Ym5GS1RBPT06ZWYzNjQ4MmM=

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_text(documents[0].page_content)
print(len(texts))
print('1111111111111111',texts[0])
print('2222222222222222',texts[1])
