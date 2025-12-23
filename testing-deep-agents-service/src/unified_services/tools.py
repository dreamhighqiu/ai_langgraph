"""统一服务的 LangChain 工具封装.

将 unified_services 中的功能封装为 LangChain 工具，
可以被智能体（Agent）直接调用。

使用示例：
    from unified_services.tools import (
        knowledge_tools,
        milvus_tools,
        minio_tools,
    )
    
    # 创建智能体
    agent = create_react_agent(llm, tools=knowledge_tools + milvus_tools)
"""

import json
import logging
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool, StructuredTool

logger = logging.getLogger(__name__)


# =============================================================================
# 知识库工具
# =============================================================================

class QueryKnowledgeInput(BaseModel):
    """查询知识库输入."""
    question: str = Field(..., description="要查询的问题")
    mode: str = Field("hybrid", description="查询模式: naive, local, global, hybrid, mix")
    top_k: int = Field(5, description="返回结果数量", ge=1, le=20)


@tool(args_schema=QueryKnowledgeInput)
async def query_knowledge_base(
    question: str,
    mode: str = "hybrid",
    top_k: int = 5,
) -> str:
    """查询知识库获取相关信息.
    
    使用这个工具从知识库中搜索与问题相关的信息。
    支持多种查询模式：
    - naive: 简单语义搜索
    - local: 本地图检索
    - global: 全局图检索  
    - hybrid: 混合检索（推荐）
    - mix: 混合模式
    
    返回相关的答案和来源信息。
    """
    try:
        from unified_services.knowledge_service import KnowledgeService, QueryMode
        
        service = KnowledgeService.get_instance()
        query_mode = QueryMode(mode) if mode in [m.value for m in QueryMode] else QueryMode.HYBRID
        
        result = await service.query(
            question=question,
            mode=query_mode,
            top_k=top_k,
        )
        
        return json.dumps({
            "answer": result.answer,
            "sources": result.sources[:3],  # 限制来源数量
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Query knowledge base failed: {e}")
        return f"查询知识库失败: {str(e)}"


class QueryDataInput(BaseModel):
    """查询原始数据输入."""
    question: str = Field(..., description="查询问题")
    mode: str = Field("naive", description="查询模式")
    top_k: int = Field(5, description="返回数量")


@tool(args_schema=QueryDataInput)
async def query_knowledge_data(
    question: str,
    mode: str = "naive",
    top_k: int = 5,
) -> str:
    """查询知识库获取原始数据（实体、关系、文档块）.
    
    当需要获取详细的知识图谱信息时使用这个工具。
    返回：
    - entities: 相关实体
    - relationships: 实体之间的关系
    - chunks: 相关文档块
    """
    try:
        from unified_services.knowledge_service import KnowledgeService, QueryMode
        
        service = KnowledgeService.get_instance()
        query_mode = QueryMode(mode) if mode in [m.value for m in QueryMode] else QueryMode.NAIVE
        
        result = await service.query_with_data(
            question=question,
            mode=query_mode,
            top_k=top_k,
        )
        
        return json.dumps({
            "entities": result.entities[:10],
            "relationships": result.relationships[:10],
            "chunks": [c.get("content", "")[:500] for c in result.chunks[:5]],
        }, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Query knowledge data failed: {e}")
        return f"查询数据失败: {str(e)}"


@tool
async def list_knowledge_bases() -> str:
    """列出所有可用的知识库.
    
    返回知识库列表，包含名称、文档数量等信息。
    """
    try:
        from unified_services.knowledge_service import KnowledgeService
        
        service = KnowledgeService.get_instance()
        kbs = await service.list_knowledge_bases()
        
        return json.dumps([
            {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "document_count": kb.document_count,
            }
            for kb in kbs
        ], ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"List knowledge bases failed: {e}")
        return f"获取知识库列表失败: {str(e)}"


# =============================================================================
# Milvus 工具
# =============================================================================

@tool
def list_milvus_collections() -> str:
    """列出所有 Milvus 向量数据库集合.
    
    返回集合列表，包含名称、向量数量等信息。
    """
    try:
        from unified_services.milvus_service import MilvusService
        
        service = MilvusService.get_instance()
        collections = service.get_all_collections_info()
        
        return json.dumps(collections, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"List Milvus collections failed: {e}")
        return f"获取集合列表失败: {str(e)}"


class CreateCollectionInput(BaseModel):
    """创建集合输入."""
    name: str = Field(..., description="集合名称")
    dimension: int = Field(1024, description="向量维度")
    description: str = Field("", description="描述")


@tool(args_schema=CreateCollectionInput)
def create_milvus_collection(
    name: str,
    dimension: int = 1024,
    description: str = "",
) -> str:
    """创建新的 Milvus 向量数据库集合.
    
    用于存储向量数据，支持语义搜索。
    """
    try:
        from unified_services.milvus_service import MilvusService
        
        service = MilvusService.get_instance()
        info = service.create_collection(name, dimension, description)
        
        return f"集合 '{name}' 创建成功，维度: {dimension}"
        
    except Exception as e:
        logger.error(f"Create collection failed: {e}")
        return f"创建集合失败: {str(e)}"


class VectorSearchInput(BaseModel):
    """向量搜索输入."""
    collection_name: str = Field(..., description="集合名称")
    query_vector: List[float] = Field(..., description="查询向量")
    limit: int = Field(10, description="返回数量")


@tool(args_schema=VectorSearchInput)
def search_vectors(
    collection_name: str,
    query_vector: List[float],
    limit: int = 10,
) -> str:
    """在 Milvus 集合中搜索相似向量.
    
    根据查询向量找到最相似的向量及其关联数据。
    """
    try:
        from unified_services.milvus_service import MilvusService
        
        service = MilvusService.get_instance()
        results = service.search(
            collection_name=collection_name,
            query_vectors=[query_vector],
            limit=limit,
        )
        
        formatted = []
        for batch in results:
            for r in batch:
                formatted.append({
                    "id": r.id,
                    "score": r.score,
                    "text": r.text,
                })
        
        return json.dumps(formatted, ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"Vector search failed: {e}")
        return f"向量搜索失败: {str(e)}"


# =============================================================================
# MinIO 工具
# =============================================================================

@tool
def list_minio_buckets() -> str:
    """列出所有 MinIO 存储桶.
    
    返回存储桶列表。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        buckets = service.list_buckets()
        
        return json.dumps([
            {
                "name": b.name,
                "created_at": b.created_at.isoformat() if b.created_at else None,
            }
            for b in buckets
        ], ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"List MinIO buckets failed: {e}")
        return f"获取存储桶列表失败: {str(e)}"


class ListFilesInput(BaseModel):
    """列出文件输入."""
    bucket_name: str = Field(..., description="存储桶名称")
    prefix: str = Field("", description="文件前缀过滤")


@tool(args_schema=ListFilesInput)
def list_files_in_bucket(
    bucket_name: str,
    prefix: str = "",
) -> str:
    """列出 MinIO 存储桶中的文件.
    
    返回文件列表，包含名称、大小等信息。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        objects = service.list_objects(bucket_name, prefix, recursive=True)
        
        return json.dumps([
            {
                "name": obj.name,
                "size": obj.size,
                "size_human": f"{obj.size / 1024 / 1024:.2f} MB" if obj.size > 1024*1024 else f"{obj.size / 1024:.2f} KB",
                "content_type": obj.content_type,
            }
            for obj in objects[:50]  # 限制数量
        ], ensure_ascii=False, indent=2)
        
    except Exception as e:
        logger.error(f"List files failed: {e}")
        return f"获取文件列表失败: {str(e)}"


class GetFileUrlInput(BaseModel):
    """获取文件URL输入."""
    bucket_name: str = Field(..., description="存储桶名称")
    object_name: str = Field(..., description="文件名称")
    expires_hours: int = Field(24, description="URL有效期（小时）")


@tool(args_schema=GetFileUrlInput)
def get_file_download_url(
    bucket_name: str,
    object_name: str,
    expires_hours: int = 24,
) -> str:
    """获取文件的下载 URL.
    
    生成临时的预签名下载 URL。
    """
    try:
        from unified_services.minio_service import MinIOService
        
        service = MinIOService.get_instance()
        url = service.get_presigned_url(object_name, bucket_name, expires_hours)
        
        return f"下载链接（{expires_hours}小时有效）: {url}"
        
    except Exception as e:
        logger.error(f"Get file URL failed: {e}")
        return f"获取文件URL失败: {str(e)}"


# =============================================================================
# 工具集合
# =============================================================================

# 知识库相关工具
knowledge_tools = [
    query_knowledge_base,
    query_knowledge_data,
    list_knowledge_bases,
]

# Milvus 向量数据库工具
milvus_tools = [
    list_milvus_collections,
    create_milvus_collection,
    search_vectors,
]

# MinIO 对象存储工具
minio_tools = [
    list_minio_buckets,
    list_files_in_bucket,
    get_file_download_url,
]

# 所有工具
all_tools = knowledge_tools + milvus_tools + minio_tools

__all__ = [
    # 知识库工具
    "query_knowledge_base",
    "query_knowledge_data",
    "list_knowledge_bases",
    "knowledge_tools",
    # Milvus 工具
    "list_milvus_collections",
    "create_milvus_collection",
    "search_vectors",
    "milvus_tools",
    # MinIO 工具
    "list_minio_buckets",
    "list_files_in_bucket",
    "get_file_download_url",
    "minio_tools",
    # 全部
    "all_tools",
]
