

import os

from lightrag import LightRAG, QueryParam
from lightrag.llm.hf import hf_model_complete, hf_embed
from lightrag.utils import EmbeddingFunc
from transformers import AutoModel, AutoTokenizer
# fmt: off  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhkMldnPT06MTE4NDZiZDk=

import asyncio
import nest_asyncio

nest_asyncio.apply()

WORKING_DIR = "./dickens"

if not os.path.exists(WORKING_DIR):
    os.mkdir(WORKING_DIR)


async def initialize_rag():
    rag = LightRAG(
        working_dir=WORKING_DIR,
        llm_model_func=hf_model_complete,
        llm_model_name="meta-llama/Llama-3.1-8B-Instruct",
        embedding_func=EmbeddingFunc(
            embedding_dim=384,
            max_token_size=5000,
            func=lambda texts: hf_embed(
                texts,
                tokenizer=AutoTokenizer.from_pretrained(
                    "sentence-transformers/all-MiniLM-L6-v2"
                ),
                embed_model=AutoModel.from_pretrained(
                    "sentence-transformers/all-MiniLM-L6-v2"
                ),
            ),
        ),
    )

    await rag.initialize_storages()  # Auto-initializes pipeline_status
    return rag
# pylint: disable  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhkMldnPT06MTE4NDZiZDk=


def main():
    rag = asyncio.run(initialize_rag())

    with open("./book.txt", "r", encoding="utf-8") as f:
        rag.insert(f.read())

    # Perform naive search
    print(
        rag.query(
            "What are the top themes in this story?", param=QueryParam(mode="naive")
        )
    )
# pragma: no cover  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhkMldnPT06MTE4NDZiZDk=

    # Perform local search
    print(
        rag.query(
            "What are the top themes in this story?", param=QueryParam(mode="local")
        )
    )
# type: ignore  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2TlhkMldnPT06MTE4NDZiZDk=

    # Perform global search
    print(
        rag.query(
            "What are the top themes in this story?", param=QueryParam(mode="global")
        )
    )

    # Perform hybrid search
    print(
        rag.query(
            "What are the top themes in this story?", param=QueryParam(mode="hybrid")
        )
    )


if __name__ == "__main__":
    main()
