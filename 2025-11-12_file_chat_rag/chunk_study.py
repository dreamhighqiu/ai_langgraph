"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

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
