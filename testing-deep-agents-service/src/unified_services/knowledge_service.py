"""知识库服务 - 整合 LightRAG 和向量存储.

提供知识库的综合管理功能：
- 知识库 CRUD 操作
- 文档上传和处理
- 语义搜索和问答
- 与 Milvus 和 MinIO 的集成
"""

import os
import json
import logging
import httpx
from typing import Optional, List, Dict, Any, BinaryIO
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

# LightRAG API 配置
LIGHTRAG_API_URL = os.getenv("LIGHTRAG_API_URL", "http://localhost:9621")
LIGHTRAG_API_KEY = os.getenv("LIGHTRAG_API_KEY", "")


class QueryMode(str, Enum):
    """查询模式."""
    NAIVE = "naive"       # 简单检索
    LOCAL = "local"       # 本地图检索
    GLOBAL = "global"     # 全局图检索
    HYBRID = "hybrid"     # 混合检索
    MIX = "mix"           # 混合模式


class UploadMode(str, Enum):
    """上传模式."""
    INGEST = "ingest"           # 入库：解析并存入知识库
    DIRECT_QA = "direct_qa"     # 直接问答：不入库，临时解析后问答


@dataclass
class KnowledgeBase:
    """知识库信息."""
    id: str
    name: str
    description: str = ""
    collection_name: str = ""
    document_count: int = 0
    entity_count: int = 0
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """文档信息."""
    id: str
    filename: str
    file_size: int = 0
    content_type: str = ""
    status: str = "pending"
    chunk_count: int = 0
    created_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class QueryResult:
    """查询结果."""
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    entities: List[Dict[str, Any]] = field(default_factory=list)
    relationships: List[Dict[str, Any]] = field(default_factory=list)
    chunks: List[Dict[str, Any]] = field(default_factory=list)


class KnowledgeService:
    """知识库服务.
    
    提供两种使用模式：
    1. 单例模式：KnowledgeService.get_instance()
    2. 实例模式：KnowledgeService(api_url=...)
    """
    
    _instance: Optional["KnowledgeService"] = None
    
    @classmethod
    def get_instance(cls) -> "KnowledgeService":
        """获取单例实例."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(
        self,
        api_url: str = LIGHTRAG_API_URL,
        api_key: str = LIGHTRAG_API_KEY,
        timeout: float = 60.0,
    ):
        """初始化知识库服务.
        
        Args:
            api_url: LightRAG API 地址
            api_key: API 密钥
            timeout: 请求超时时间
        """
        self.api_url = api_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """获取 HTTP 客户端."""
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["X-API-Key"] = self.api_key
            self._client = httpx.AsyncClient(
                base_url=self.api_url,
                headers=headers,
                timeout=self.timeout,
            )
        return self._client
    
    async def close(self):
        """关闭客户端连接."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # =========================================================================
    # 知识库管理
    # =========================================================================
    
    async def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """列出所有知识库.
        
        注意: LightRAG 默认单知识库模式，这里返回默认知识库。
        多知识库需要通过不同的存储路径或 workspace 实现。
        """
        try:
            client = await self._get_client()
            
            # 获取状态统计
            status_response = await client.get("/documents/status_counts")
            stats = status_response.json() if status_response.is_success else {}
            
            # 获取文档数量
            doc_response = await client.post("/documents/paginated", json={
                "page": 1,
                "page_size": 1,
            })
            doc_data = doc_response.json() if doc_response.is_success else {}
            
            total_docs = doc_data.get("total", 0)
            status_counts = stats.get("status_counts", stats)
            
            default_kb = KnowledgeBase(
                id="default",
                name="默认知识库",
                description="LightRAG 默认知识库",
                collection_name="default",
                document_count=total_docs,
                entity_count=status_counts.get("completed", 0),
                status="active",
                metadata={"status_counts": status_counts},
            )
            
            return [default_kb]
            
        except Exception as e:
            logger.error(f"Failed to list knowledge bases: {e}")
            raise RuntimeError(f"列出知识库失败: {e}")
    
    async def get_knowledge_base(self, kb_id: str = "default") -> KnowledgeBase:
        """获取知识库详情."""
        kbs = await self.list_knowledge_bases()
        for kb in kbs:
            if kb.id == kb_id:
                return kb
        raise ValueError(f"知识库 '{kb_id}' 不存在")
    
    async def get_stats(self, kb_id: str = "default") -> Dict[str, Any]:
        """获取知识库统计信息."""
        try:
            client = await self._get_client()
            
            # 获取状态统计
            status_response = await client.get("/documents/status_counts")
            status_data = status_response.json() if status_response.is_success else {}
            
            # 获取最近文档
            doc_response = await client.post("/documents/paginated", json={
                "page": 1,
                "page_size": 10,
            })
            doc_data = doc_response.json() if doc_response.is_success else {}
            
            return {
                "kb_id": kb_id,
                "total_documents": doc_data.get("total", 0),
                "status_counts": status_data.get("status_counts", status_data),
                "recent_documents": doc_data.get("documents", [])[:5],
            }
            
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            raise RuntimeError(f"获取统计信息失败: {e}")
    
    # =========================================================================
    # 文档管理
    # =========================================================================
    
    async def upload_document(
        self,
        file_data: bytes,
        filename: str,
        mode: UploadMode = UploadMode.INGEST,
        kb_id: str = "default",
        content_type: str = "application/octet-stream",
    ) -> Document:
        """上传文档.
        
        Args:
            file_data: 文件数据
            filename: 文件名
            mode: 上传模式
            kb_id: 知识库 ID
            content_type: 内容类型
        """
        try:
            client = await self._get_client()
            
            if mode == UploadMode.INGEST:
                files = {"file": (filename, file_data, content_type)}
                response = await client.post("/documents/upload", files=files)
                
                if not response.is_success:
                    error = response.json() if response.text else {"detail": "上传失败"}
                    raise RuntimeError(error.get("detail", "上传失败"))
                
                result = response.json()
                
                return Document(
                    id=result.get("document_id", filename),
                    filename=filename,
                    file_size=len(file_data),
                    content_type=content_type,
                    status=result.get("status", "processing"),
                    chunk_count=result.get("chunks_count", 0),
                )
            else:
                # 直接问答模式：返回临时文档信息
                return Document(
                    id=f"temp_{filename}_{datetime.now().timestamp()}",
                    filename=filename,
                    file_size=len(file_data),
                    content_type=content_type,
                    status="temp",
                )
                
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            raise RuntimeError(f"上传文档失败: {e}")
    
    async def list_documents(
        self,
        kb_id: str = "default",
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> Dict[str, Any]:
        """列出文档."""
        try:
            client = await self._get_client()
            
            payload = {"page": page, "page_size": page_size}
            if status:
                payload["status"] = status
            
            response = await client.post("/documents/paginated", json=payload)
            
            if not response.is_success:
                raise RuntimeError("获取文档列表失败")
            
            data = response.json()
            
            return {
                "documents": data.get("documents", []),
                "total": data.get("total", 0),
                "page": page,
                "page_size": page_size,
                "total_pages": (data.get("total", 0) + page_size - 1) // page_size,
            }
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            raise RuntimeError(f"列出文档失败: {e}")
    
    async def delete_document(self, doc_id: str, kb_id: str = "default") -> bool:
        """删除文档."""
        try:
            client = await self._get_client()
            
            response = await client.delete(
                "/documents/delete_document",
                params={"doc_id": doc_id},
            )
            
            if not response.is_success:
                error = response.json() if response.text else {"detail": "删除失败"}
                raise RuntimeError(error.get("detail", "删除失败"))
            
            logger.info(f"Deleted document: {doc_id}")
            return True
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            raise RuntimeError(f"删除文档失败: {e}")
    
    async def get_document_status(self, doc_id: str) -> Dict[str, Any]:
        """获取文档处理状态."""
        try:
            client = await self._get_client()
            response = await client.get(f"/documents/track_status/{doc_id}")
            
            if not response.is_success:
                raise RuntimeError("获取文档状态失败")
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get document status: {e}")
            raise RuntimeError(f"获取文档状态失败: {e}")
    
    # =========================================================================
    # 查询功能
    # =========================================================================
    
    async def query(
        self,
        question: str,
        mode: QueryMode = QueryMode.HYBRID,
        kb_id: str = "default",
        top_k: int = 5,
        only_context: bool = False,
    ) -> QueryResult:
        """查询知识库.
        
        Args:
            question: 问题
            mode: 查询模式
            kb_id: 知识库 ID
            top_k: 返回结果数量
            only_context: 只返回上下文，不生成回答
        """
        try:
            client = await self._get_client()
            
            payload = {
                "query": question,
                "mode": mode.value,
                "top_k": top_k,
                "only_need_context": only_context,
            }
            
            response = await client.post("/query/query", json=payload)
            
            if not response.is_success:
                error = response.json() if response.text else {"detail": "查询失败"}
                raise RuntimeError(error.get("detail", "查询失败"))
            
            data = response.json()
            
            return QueryResult(
                answer=data.get("response", ""),
                sources=data.get("sources", []),
            )
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to query: {e}")
            raise RuntimeError(f"查询失败: {e}")
    
    async def query_with_data(
        self,
        question: str,
        mode: QueryMode = QueryMode.NAIVE,
        top_k: int = 5,
    ) -> QueryResult:
        """查询知识库并返回原始数据（实体、关系、文档块）."""
        try:
            client = await self._get_client()
            
            payload = {
                "query": question,
                "mode": mode.value,
                "top_k": top_k,
            }
            
            response = await client.post("/query/data", json=payload)
            
            if not response.is_success:
                error = response.json() if response.text else {"detail": "查询失败"}
                raise RuntimeError(error.get("detail", "查询失败"))
            
            data = response.json()
            
            return QueryResult(
                answer="",  # /query/data 不返回生成的回答
                entities=data.get("entities", []),
                relationships=data.get("relationships", []),
                chunks=data.get("chunks", []),
            )
            
        except RuntimeError:
            raise
        except Exception as e:
            logger.error(f"Failed to query data: {e}")
            raise RuntimeError(f"查询数据失败: {e}")
    
    async def query_stream(
        self,
        question: str,
        mode: QueryMode = QueryMode.HYBRID,
        top_k: int = 5,
    ):
        """流式查询知识库."""
        try:
            client = await self._get_client()
            
            payload = {
                "query": question,
                "mode": mode.value,
                "top_k": top_k,
            }
            
            async with client.stream("POST", "/query/stream", json=payload) as response:
                async for chunk in response.aiter_text():
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Failed to stream query: {e}")
            raise RuntimeError(f"流式查询失败: {e}")
    
    # =========================================================================
    # 图谱操作
    # =========================================================================
    
    async def get_graph_labels(self) -> List[str]:
        """获取图谱标签列表."""
        try:
            client = await self._get_client()
            response = await client.get("/graph/label/list")
            
            if not response.is_success:
                return []
            
            data = response.json()
            return data.get("labels", [])
            
        except Exception as e:
            logger.error(f"Failed to get graph labels: {e}")
            return []
    
    async def get_knowledge_graph(
        self,
        label: Optional[str] = None,
        max_depth: int = 2,
    ) -> Dict[str, Any]:
        """获取知识图谱."""
        try:
            client = await self._get_client()
            
            params = {"max_depth": max_depth}
            if label:
                params["label"] = label
            
            response = await client.get("/graphs", params=params)
            
            if not response.is_success:
                return {"nodes": [], "edges": []}
            
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get knowledge graph: {e}")
            return {"nodes": [], "edges": []}
    
    # =========================================================================
    # 健康检查
    # =========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查."""
        try:
            client = await self._get_client()
            
            # 简单测试 API 可用性
            response = await client.get("/documents/status_counts")
            
            if response.is_success:
                return {
                    "status": "healthy",
                    "api_url": self.api_url,
                }
            else:
                return {
                    "status": "unhealthy",
                    "api_url": self.api_url,
                    "error": f"API returned {response.status_code}",
                }
                
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_url": self.api_url,
                "error": str(e),
            }
