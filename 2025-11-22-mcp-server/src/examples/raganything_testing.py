"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio

from lightrag.llm.ollama import ollama_embed
from raganything import RAGAnything, RAGAnythingConfig
from lightrag.llm.openai import openai_complete_if_cache, openai_embed
from lightrag.utils import EmbeddingFunc

# one-api API Key
ONE_API_KEY= "sk-0DSjgogbOJdMmIBv476a4aF9431b4f15B70dC093Aa15A2Ac"

# one-api 服务地址
ONE_API_BASE_URL="http://47.253.63.85:3000/v1"

async def main():
    # 设置 API 配置
    api_key = "sk-0DSjgogbOJdMmIBv476a4aF9431b4f15B70dC093Aa15A2Ac"
    base_url = "http://47.253.63.85:3000/v1"  # 可选
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVZSMFp3PT06M2Q2MGNiZjc=

    vm_api_key = "sk-0DSjgogbOJdMmIBv476a4aF9431b4f15B70dC093Aa15A2Ac"
    vm_base_url = "http://47.253.63.85:3000/v1"
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVZSMFp3PT06M2Q2MGNiZjc=
     
    ollama_url='http://54.179.103.192:11434/'

    # 创建 RAGAnything 配置
    config = RAGAnythingConfig(
        working_dir="./rag_storage",
        parser="docling",  # 选择解析器：mineru 或 docling
        parse_method="auto",  # 解析方法：auto, ocr 或 txt
        enable_image_processing=True,
        enable_table_processing=True,
        enable_equation_processing=True,
    )

    # 定义 LLM 模型函数
    def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
        return openai_complete_if_cache(
            "deepseek-chat",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=api_key,
            base_url=base_url,
            **kwargs,
        )

    # 定义视觉模型函数用于图像处理
    def vision_model_func(
        prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
    ):
        # 如果提供了messages格式（用于多模态VLM增强查询），直接使用
        if messages:
            return openai_complete_if_cache(
                "gpt-4o",
                "",
                system_prompt=None,
                history_messages=[],
                messages=messages,
                api_key=vm_api_key,
                base_url=vm_base_url,
                **kwargs,
            )
        # 传统单图片格式
        elif image_data:
            return openai_complete_if_cache(
                "doubao-seed-1-6-251015",
                "",
                system_prompt=None,
                history_messages=[],
                messages=[
                    {"role": "system", "content": system_prompt}
                    if system_prompt
                    else None,
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                        ],
                    }
                    if image_data
                    else {"role": "user", "content": prompt},
                ],
                api_key=vm_api_key,
                base_url=vm_base_url,
                **kwargs,
            )
        # 纯文本格式
        else:
            return llm_model_func(prompt, system_prompt, history_messages, **kwargs)
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVZSMFp3PT06M2Q2MGNiZjc=

    # 定义嵌入函数
    embedding_func = EmbeddingFunc(
        embedding_dim=1024,
        max_token_size=32000,
        func=lambda texts: ollama_embed(
            texts,
            embed_model="qwen3-embedding:0.6b",
            api_key="sk-danwen",
            host=ollama_url,
        ),
    )

    # 初始化 RAGAnything - 添加 LightRAG 配置以优化性能和超时
    rag = RAGAnything(
        config=config,
        llm_model_func=llm_model_func,
        vision_model_func=vision_model_func,
        embedding_func=embedding_func,
        lightrag_kwargs={
            # 优化chunk大小以加快处理
            "chunk_token_size": 1200,
            "chunk_overlap_token_size": 100,
            "tiktoken_model_name": "gpt-4o",
            # 增加超时时间以处理大文档
            "default_embedding_timeout": 300,  # 嵌入超时：5分钟
            "default_llm_timeout": 300,  # LLM超时：5分钟
            # 减少并发以避免超时
            "embedding_func_max_async": 4,  # 减少并发嵌入请求
            "llm_model_max_async": 2,  # 减少并发LLM请求
        }
    )

    # 处理文档
    await rag.process_document_complete(
        file_path="llm_course.pdf",
        output_dir="./output",
        parse_method="auto"
    )

    # 查询处理后的内容
    # 纯文本查询 - 基本知识库搜索
    text_result = await rag.aquery(
        "文档的主要内容是什么？",
        mode="hybrid"
    )
    print("文本查询结果:", text_result)

    # 多模态查询 - 包含具体多模态内容的查询
    multimodal_result = await rag.aquery_with_multimodal(
        "分析这个性能数据并解释与现有文档内容的关系",
        multimodal_content=[{
            "type": "table",
            "table_data": """系统,准确率,F1分数
                            RAGAnything,95.2%,0.94
                            基准方法,87.3%,0.85""",
            "table_caption": "性能对比结果"
        }],
        mode="hybrid"
    )
    print("多模态查询结果:", multimodal_result)
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2UVZSMFp3PT06M2Q2MGNiZjc=

if __name__ == "__main__":
    asyncio.run(main())