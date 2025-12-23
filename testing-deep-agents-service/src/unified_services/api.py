"""统一服务 API - FastAPI 路由.

提供统一的 REST API，整合：
- 知识库管理 (Knowledge Base)
- Milvus 向量数据库管理
- MinIO 对象存储管理
- 数据库操作
- 健康检查

API 前缀: /api/v1/services
"""

import os
import logging
from typing import Optional, List
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from pydantic import BaseModel, Field
from enum import Enum

from unified_services.milvus_service import MilvusService
from unified_services.minio_service import MinIOService
from unified_services.knowledge_service import KnowledgeService, QueryMode, UploadMode
from unified_services.database_service import DatabaseService

logger = logging.getLogger(__name__)

# 创建路由器
router = APIRouter(prefix="/api/v1/services", tags=["Unified Services"])


# =============================================================================
# Pydantic 模型
# =============================================================================

class CreateCollectionRequest(BaseModel):
    """创建 Collection 请求."""
    name: str = Field(..., description="Collection 名称")
    description: str = Field("", description="描述")
    dimension: int = Field(1024, description="向量维度")
    metric_type: str = Field("COSINE", description="距离度量类型")


class CreateBucketRequest(BaseModel):
    """创建 Bucket 请求."""
    name: str = Field(..., description="Bucket 名称")


class QueryRequest(BaseModel):
    """知识库查询请求."""
    question: str = Field(..., description="问题")
    mode: str = Field("hybrid", description="查询模式: naive, local, global, hybrid, mix")
    top_k: int = Field(5, description="返回结果数量")
    only_context: bool = Field(False, description="只返回上下文")


class VectorSearchRequest(BaseModel):
    """向量搜索请求."""
    collection_name: str = Field(..., description="Collection 名称")
    vectors: List[List[float]] = Field(..., description="查询向量")
    limit: int = Field(10, description="返回数量")
    output_fields: Optional[List[str]] = Field(None, description="返回字段")
    filter_expr: Optional[str] = Field(None, description="过滤表达式")


class ApiResponse(BaseModel):
    """通用 API 响应."""
    success: bool = True
    message: str = ""
    data: Optional[dict] = None


# =============================================================================
# 依赖注入
# =============================================================================

def get_milvus_service() -> MilvusService:
    """获取 Milvus 服务实例."""
    return MilvusService.get_instance()


def get_minio_service() -> MinIOService:
    """获取 MinIO 服务实例."""
    return MinIOService.get_instance()


def get_knowledge_service() -> KnowledgeService:
    """获取知识库服务实例."""
    return KnowledgeService.get_instance()


def get_database_service() -> DatabaseService:
    """获取数据库服务实例."""
    return DatabaseService.get_instance()


# =============================================================================
# 知识库 API
# =============================================================================

@router.get("/knowledge/list", summary="列出所有知识库")
async def list_knowledge_bases(
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """列出所有知识库."""
    try:
        kbs = await service.list_knowledge_bases()
        return {
            "success": True,
            "data": {
                "knowledge_bases": [
                    {
                        "id": kb.id,
                        "name": kb.name,
                        "description": kb.description,
                        "document_count": kb.document_count,
                        "entity_count": kb.entity_count,
                        "status": kb.status,
                        "metadata": kb.metadata,
                    }
                    for kb in kbs
                ]
            }
        }
    except Exception as e:
        logger.error(f"Failed to list knowledge bases: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{kb_id}", summary="获取知识库详情")
async def get_knowledge_base(
    kb_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取知识库详情."""
    try:
        kb = await service.get_knowledge_base(kb_id)
        return {
            "success": True,
            "data": {
                "id": kb.id,
                "name": kb.name,
                "description": kb.description,
                "document_count": kb.document_count,
                "entity_count": kb.entity_count,
                "status": kb.status,
                "metadata": kb.metadata,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{kb_id}/stats", summary="获取知识库统计")
async def get_knowledge_stats(
    kb_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """获取知识库统计信息."""
    try:
        stats = await service.get_stats(kb_id)
        return {"success": True, "data": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge/{kb_id}/documents", summary="列出文档")
async def list_documents(
    kb_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """列出知识库中的文档."""
    try:
        result = await service.list_documents(kb_id, page, page_size, status)
        return {"success": True, "data": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/{kb_id}/upload", summary="上传文档")
async def upload_document(
    kb_id: str,
    file: UploadFile = File(...),
    mode: str = Form("ingest"),
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """上传文档到知识库.
    
    - mode=ingest: 入库模式
    - mode=direct_qa: 直接问答模式（不入库）
    """
    try:
        file_data = await file.read()
        upload_mode = UploadMode.INGEST if mode == "ingest" else UploadMode.DIRECT_QA
        
        doc = await service.upload_document(
            file_data=file_data,
            filename=file.filename or "unknown",
            mode=upload_mode,
            kb_id=kb_id,
            content_type=file.content_type or "application/octet-stream",
        )
        
        return {
            "success": True,
            "data": {
                "id": doc.id,
                "filename": doc.filename,
                "file_size": doc.file_size,
                "status": doc.status,
                "chunk_count": doc.chunk_count,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/knowledge/{kb_id}/documents/{doc_id}", summary="删除文档")
async def delete_document(
    kb_id: str,
    doc_id: str,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """删除文档."""
    try:
        await service.delete_document(doc_id, kb_id)
        return {"success": True, "message": f"文档 {doc_id} 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/{kb_id}/query", summary="查询知识库")
async def query_knowledge_base(
    kb_id: str,
    request: QueryRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """查询知识库."""
    try:
        mode = QueryMode(request.mode) if request.mode in [m.value for m in QueryMode] else QueryMode.HYBRID
        
        result = await service.query(
            question=request.question,
            mode=mode,
            kb_id=kb_id,
            top_k=request.top_k,
            only_context=request.only_context,
        )
        
        return {
            "success": True,
            "data": {
                "answer": result.answer,
                "sources": result.sources,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/knowledge/{kb_id}/query/data", summary="查询原始数据")
async def query_knowledge_data(
    kb_id: str,
    request: QueryRequest,
    service: KnowledgeService = Depends(get_knowledge_service),
):
    """查询知识库原始数据（实体、关系、文档块）."""
    try:
        mode = QueryMode(request.mode) if request.mode in [m.value for m in QueryMode] else QueryMode.NAIVE
        
        result = await service.query_with_data(
            question=request.question,
            mode=mode,
            top_k=request.top_k,
        )
        
        return {
            "success": True,
            "data": {
                "entities": result.entities,
                "relationships": result.relationships,
                "chunks": result.chunks,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Milvus API
# =============================================================================

@router.get("/milvus/collections", summary="列出 Collections")
async def list_collections(
    service: MilvusService = Depends(get_milvus_service),
):
    """列出所有 Milvus collections."""
    try:
        collections = service.get_all_collections_info()
        return {"success": True, "data": {"collections": collections}}
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/milvus/collections/{name}", summary="获取 Collection 详情")
async def get_collection(
    name: str,
    service: MilvusService = Depends(get_milvus_service),
):
    """获取 collection 详情."""
    try:
        info = service.get_collection_info(name)
        return {
            "success": True,
            "data": {
                "name": info.name,
                "description": info.description,
                "num_entities": info.num_entities,
                "dimension": info.dimension,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/milvus/collections", summary="创建 Collection")
async def create_collection(
    request: CreateCollectionRequest,
    service: MilvusService = Depends(get_milvus_service),
):
    """创建新的 collection."""
    try:
        info = service.create_collection(
            collection_name=request.name,
            dimension=request.dimension,
            description=request.description,
            metric_type=request.metric_type,
        )
        return {
            "success": True,
            "message": f"Collection '{request.name}' 创建成功",
            "data": {
                "name": info.name,
                "dimension": info.dimension,
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/milvus/collections/{name}", summary="删除 Collection")
async def delete_collection(
    name: str,
    service: MilvusService = Depends(get_milvus_service),
):
    """删除 collection."""
    try:
        service.drop_collection(name)
        return {"success": True, "message": f"Collection '{name}' 已删除"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/milvus/search", summary="向量搜索")
async def vector_search(
    request: VectorSearchRequest,
    service: MilvusService = Depends(get_milvus_service),
):
    """在 collection 中搜索相似向量."""
    try:
        results = service.search(
            collection_name=request.collection_name,
            query_vectors=request.vectors,
            limit=request.limit,
            output_fields=request.output_fields,
            filter_expr=request.filter_expr,
        )
        
        return {
            "success": True,
            "data": {
                "results": [
                    [
                        {"id": r.id, "score": r.score, "text": r.text, "metadata": r.metadata}
                        for r in batch
                    ]
                    for batch in results
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# MinIO API
# =============================================================================

@router.get("/minio/buckets", summary="列出 Buckets")
async def list_buckets(
    service: MinIOService = Depends(get_minio_service),
):
    """列出所有 MinIO buckets."""
    try:
        buckets = service.list_buckets()
        return {
            "success": True,
            "data": {
                "buckets": [
                    {
                        "name": b.name,
                        "created_at": b.created_at.isoformat() if b.created_at else None,
                    }
                    for b in buckets
                ]
            }
        }
    except ConnectionError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minio/buckets/{name}", summary="获取 Bucket 统计")
async def get_bucket_stats(
    name: str,
    service: MinIOService = Depends(get_minio_service),
):
    """获取 bucket 统计信息."""
    try:
        stats = service.get_bucket_stats(name)
        return {"success": True, "data": stats}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/minio/buckets", summary="创建 Bucket")
async def create_bucket(
    request: CreateBucketRequest,
    service: MinIOService = Depends(get_minio_service),
):
    """创建 bucket."""
    try:
        bucket = service.create_bucket(request.name)
        return {
            "success": True,
            "message": f"Bucket '{request.name}' 创建成功",
            "data": {"name": bucket.name}
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/minio/buckets/{name}", summary="删除 Bucket")
async def delete_bucket(
    name: str,
    force: bool = False,
    service: MinIOService = Depends(get_minio_service),
):
    """删除 bucket."""
    try:
        service.delete_bucket(name, force=force)
        return {"success": True, "message": f"Bucket '{name}' 已删除"}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minio/buckets/{bucket_name}/objects", summary="列出文件")
async def list_objects(
    bucket_name: str,
    prefix: str = "",
    recursive: bool = False,
    service: MinIOService = Depends(get_minio_service),
):
    """列出 bucket 中的文件."""
    try:
        objects = service.list_objects(bucket_name, prefix, recursive)
        return {
            "success": True,
            "data": {
                "objects": [
                    {
                        "name": obj.name,
                        "size": obj.size,
                        "content_type": obj.content_type,
                        "last_modified": obj.last_modified.isoformat() if obj.last_modified else None,
                        "is_dir": obj.is_dir,
                    }
                    for obj in objects
                ]
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/minio/buckets/{bucket_name}/upload", summary="上传文件")
async def upload_file(
    bucket_name: str,
    file: UploadFile = File(...),
    object_name: Optional[str] = Form(None),
    service: MinIOService = Depends(get_minio_service),
):
    """上传文件到 bucket."""
    try:
        import io
        
        file_data = await file.read()
        
        obj = await service.upload_file(
            file_data=io.BytesIO(file_data),
            filename=file.filename or "unknown",
            bucket_name=bucket_name,
            object_name=object_name,
            content_type=file.content_type or "application/octet-stream",
        )
        
        return {
            "success": True,
            "message": f"文件上传成功",
            "data": {
                "name": obj.name,
                "size": obj.size,
                "content_type": obj.content_type,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/minio/buckets/{bucket_name}/objects/{object_name:path}", summary="删除文件")
async def delete_object(
    bucket_name: str,
    object_name: str,
    service: MinIOService = Depends(get_minio_service),
):
    """删除文件."""
    try:
        service.delete_object(object_name, bucket_name)
        return {"success": True, "message": f"文件 '{object_name}' 已删除"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/minio/buckets/{bucket_name}/objects/{object_name:path}/url", summary="获取文件URL")
async def get_object_url(
    bucket_name: str,
    object_name: str,
    expires_hours: int = Query(24, ge=1, le=168),
    service: MinIOService = Depends(get_minio_service),
):
    """获取文件预签名 URL."""
    try:
        url = service.get_presigned_url(object_name, bucket_name, expires_hours)
        return {
            "success": True,
            "data": {
                "url": url,
                "expires_in_hours": expires_hours,
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# 健康检查
# =============================================================================

@router.get("/health", summary="服务健康检查")
async def health_check(
    milvus: MilvusService = Depends(get_milvus_service),
    minio: MinIOService = Depends(get_minio_service),
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    database: DatabaseService = Depends(get_database_service),
):
    """检查所有服务的健康状态."""
    health = {
        "milvus": milvus.health_check(),
        "minio": minio.health_check(),
        "knowledge": await knowledge.health_check(),
        "database": await database.health_check(),
    }
    
    all_healthy = all(
        s.get("status") == "healthy" 
        for s in health.values()
    )
    
    return {
        "success": all_healthy,
        "data": health,
    }


@router.get("/health/{service_name}", summary="单个服务健康检查")
async def check_service_health(
    service_name: str,
    milvus: MilvusService = Depends(get_milvus_service),
    minio: MinIOService = Depends(get_minio_service),
    knowledge: KnowledgeService = Depends(get_knowledge_service),
    database: DatabaseService = Depends(get_database_service),
):
    """检查单个服务的健康状态."""
    if service_name == "milvus":
        result = milvus.health_check()
    elif service_name == "minio":
        result = minio.health_check()
    elif service_name == "knowledge":
        result = await knowledge.health_check()
    elif service_name == "database":
        result = await database.health_check()
    else:
        raise HTTPException(status_code=404, detail=f"未知服务: {service_name}")
    
    return {"success": result.get("status") == "healthy", "data": result}

