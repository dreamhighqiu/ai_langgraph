"""Knowledge Base Query Tools.

提供给 Agent 使用的知识库查询工具，支持多种查询模式。
"""

import os
import httpx
from typing import Optional, List, Literal
from langchain_core.tools import tool


# 从环境变量获取知识库 API 地址
KNOWLEDGE_API_URL = os.getenv("KNOWLEDGE_API_URL", "http://localhost:9621")


async def _query_knowledge_base(
    query: str,
    mode: str = "mix",
    top_k: int = 10,
    only_need_context: bool = False,
    include_references: bool = True,
) -> dict:
    """内部函数：调用 LightRAG API 查询知识库。"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": query,
            "mode": mode,
            "top_k": top_k,
            "only_need_context": only_need_context,
            "include_references": include_references,
            "stream": False,
        }
        
        try:
            response = await client.post(
                f"{KNOWLEDGE_API_URL}/query",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e), "response": None}


async def _query_knowledge_data(
    query: str,
    mode: str = "mix",
    top_k: int = 10,
) -> dict:
    """内部函数：调用 LightRAG /query/data API 获取结构化数据。"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "query": query,
            "mode": mode,
            "top_k": top_k,
        }
        
        try:
            response = await client.post(
                f"{KNOWLEDGE_API_URL}/query/data",
                json=payload,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            return {"error": str(e), "status": "failure"}


@tool
async def search_knowledge(
    query: str,
    mode: Literal["local", "global", "hybrid", "naive", "mix"] = "mix",
) -> str:
    """搜索知识库获取相关信息。

    使用此工具从知识库中检索与查询相关的信息。支持多种检索模式：
    - local: 聚焦于特定实体及其直接关系
    - global: 分析知识图谱中更广泛的模式和关系  
    - hybrid: 结合 local 和 global 方法
    - naive: 仅使用向量相似度搜索
    - mix: 整合知识图谱和向量检索（推荐）

    Args:
        query: 搜索查询文本，至少3个字符
        mode: 查询模式，默认为 "mix"

    Returns:
        知识库返回的相关信息文本
    """
    result = await _query_knowledge_base(
        query=query,
        mode=mode,
        top_k=10,
        only_need_context=False,
        include_references=True,
    )
    
    if "error" in result:
        return f"查询知识库时出错: {result['error']}"
    
    response_text = result.get("response", "")
    references = result.get("references", [])
    
    # 构建返回文本
    output_parts = [response_text]
    
    if references:
        output_parts.append("\n\n---\n**参考来源:**")
        for ref in references[:5]:  # 最多显示5个参考
            file_path = ref.get("file_path", "未知来源")
            output_parts.append(f"- {file_path}")
    
    return "\n".join(output_parts)


@tool
async def get_knowledge_entities(
    query: str,
    mode: Literal["local", "global", "hybrid", "mix"] = "local",
) -> str:
    """获取知识库中与查询相关的实体和关系。

    此工具返回知识图谱中的实体、关系和文本块等结构化数据，
    适用于需要了解概念之间关系的场景。

    Args:
        query: 搜索查询文本
        mode: 查询模式，"local" 聚焦实体，"global" 聚焦关系

    Returns:
        结构化的实体和关系信息
    """
    result = await _query_knowledge_data(
        query=query,
        mode=mode,
        top_k=10,
    )
    
    if result.get("status") == "failure" or "error" in result:
        return f"查询失败: {result.get('error', result.get('message', '未知错误'))}"
    
    data = result.get("data", {})
    output_parts = []
    
    # 实体信息
    entities = data.get("entities", [])
    if entities:
        output_parts.append("## 相关概念/实体\n")
        for entity in entities[:8]:
            name = entity.get("entity_name", "")
            entity_type = entity.get("entity_type", "")
            description = entity.get("description", "")
            output_parts.append(f"- **{name}** ({entity_type}): {description}")
    
    # 关系信息
    relationships = data.get("relationships", [])
    if relationships:
        output_parts.append("\n## 关键关系\n")
        for rel in relationships[:8]:
            src = rel.get("src_id", "")
            tgt = rel.get("tgt_id", "")
            desc = rel.get("description", "")
            output_parts.append(f"- {src} → {tgt}: {desc}")
    
    # 文本块
    chunks = data.get("chunks", [])
    if chunks:
        output_parts.append("\n## 相关文档内容\n")
        for chunk in chunks[:3]:
            content = chunk.get("content", "")[:500]  # 限制长度
            file_path = chunk.get("file_path", "")
            output_parts.append(f"```\n{content}\n```")
            output_parts.append(f"_来源: {file_path}_\n")
    
    if not output_parts:
        return "未找到相关信息"
    
    return "\n".join(output_parts)


@tool
async def list_knowledge_documents() -> str:
    """列出知识库中已索引的文档。

    Returns:
        知识库中的文档列表
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{KNOWLEDGE_API_URL}/documents")
            response.raise_for_status()
            docs = response.json()
            
            if not docs:
                return "知识库中暂无文档"
            
            output_parts = ["## 知识库文档列表\n"]
            
            # 处理不同的返回格式：可能是列表或字典
            if isinstance(docs, dict):
                # 如果是字典，可能是 {filename: status} 或 {data: [...]} 格式
                doc_list = docs.get("data", docs.get("documents", list(docs.items())))
                if isinstance(doc_list, dict):
                    doc_list = list(doc_list.items())
            else:
                doc_list = docs
            
            for doc in doc_list[:20]:  # 最多显示20个
                if isinstance(doc, dict):
                    name = doc.get("name", doc.get("file_path", "未知"))
                    status = doc.get("status", "")
                    output_parts.append(f"- {name} ({status})" if status else f"- {name}")
                elif isinstance(doc, tuple):
                    # 处理 (filename, status) 元组
                    name, status = doc
                    output_parts.append(f"- {name} ({status})" if status else f"- {name}")
                else:
                    output_parts.append(f"- {doc}")
            
            return "\n".join(output_parts)
        except httpx.HTTPError as e:
            return f"获取文档列表失败: {str(e)}"


# 导出所有工具
knowledge_tools = [
    search_knowledge,
    get_knowledge_entities,
    list_knowledge_documents,
]
