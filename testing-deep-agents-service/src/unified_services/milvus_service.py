"""Milvus 向量数据库服务.

整合 Milvus 的所有操作，提供统一的接口：
- Collection 管理（创建、删除、列表）
- 向量操作（插入、搜索、删除）
- 统计信息查询

支持两种客户端模式：
1. MilvusClient (轻量级，推荐)
2. pymilvus connections (完整功能)
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import time
from pathlib import Path

# 确保在读取环境变量之前加载 .env 文件
try:
    from dotenv import load_dotenv
    # 从当前文件向上查找 .env 文件
    env_paths = [
        Path(__file__).parent.parent.parent / ".env",  # testing-deep-agents-service/.env
        Path(__file__).parent.parent.parent.parent / ".env",  # 项目根目录/.env
    ]
    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(env_path)
            break
except ImportError:
    pass

logger = logging.getLogger(__name__)

# 配置 - 在 load_dotenv() 之后读取
MILVUS_HOST = os.getenv("MILVUS_HOST", "localhost")
MILVUS_PORT = int(os.getenv("MILVUS_PORT", "19530"))
MILVUS_URI = os.getenv("MILVUS_URI", f"http://{MILVUS_HOST}:{MILVUS_PORT}")
MILVUS_USER = os.getenv("MILVUS_USER", "")
MILVUS_PASSWORD = os.getenv("MILVUS_PASSWORD", "")


@dataclass
class CollectionInfo:
    """Collection 信息."""
    name: str
    description: str = ""
    num_entities: int = 0
    num_partitions: int = 0
    dimension: int = 0
    schema_fields: List[Dict[str, Any]] = field(default_factory=list)
    index_info: Optional[Dict[str, Any]] = None
    load_state: str = "unknown"


@dataclass
class SearchResult:
    """搜索结果."""
    id: str
    score: float
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class MilvusService:
    """Milvus 向量数据库服务.
    
    提供两种使用模式：
    1. 单例模式：MilvusService.get_instance()
    2. 实例模式：MilvusService(uri=...)
    """
    
    _instance: Optional["MilvusService"] = None
    
    @classmethod
    def get_instance(cls) -> "MilvusService":
        """获取单例实例."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(
        self,
        uri: str = MILVUS_URI,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: str = MILVUS_USER,
        password: str = MILVUS_PASSWORD,
    ):
        """初始化 Milvus 服务.
        
        Args:
            uri: Milvus URI (优先使用)
            host: Milvus 主机地址
            port: Milvus 端口
            user: 用户名
            password: 密码
        """
        self.uri = uri
        self.host = host or MILVUS_HOST
        self.port = port or MILVUS_PORT
        self.user = user
        self.password = password
        self._client = None
        self._connected = False
    
    def _get_client(self):
        """获取 MilvusClient 实例."""
        if self._client is None:
            try:
                from pymilvus import MilvusClient
                self._client = MilvusClient(uri=self.uri)
                logger.info(f"Connected to Milvus at {self.uri}")
            except Exception as e:
                logger.error(f"Failed to connect to Milvus: {e}")
                raise ConnectionError(f"无法连接到 Milvus: {e}")
        return self._client
    
    def _ensure_connection(self):
        """确保已连接到 Milvus (使用 pymilvus connections)."""
        if self._connected:
            return
        
        try:
            from pymilvus import connections
            
            conn_params = {
                "alias": "default",
                "host": self.host,
                "port": self.port,
            }
            if self.user and self.password:
                conn_params["user"] = self.user
                conn_params["password"] = self.password
            
            connections.connect(**conn_params)
            self._connected = True
            logger.info(f"Connected to Milvus at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            raise ConnectionError(f"无法连接到 Milvus: {e}")
    
    def disconnect(self):
        """断开连接."""
        if self._connected:
            try:
                from pymilvus import connections
                connections.disconnect("default")
                self._connected = False
            except Exception:
                pass
        self._client = None
    
    # =========================================================================
    # Collection 管理
    # =========================================================================
    
    def list_collections(self) -> List[str]:
        """列出所有 collections."""
        try:
            client = self._get_client()
            return sorted(client.list_collections())
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            raise RuntimeError(f"列出 collections 失败: {e}")
    
    def has_collection(self, collection_name: str) -> bool:
        """检查 collection 是否存在."""
        try:
            client = self._get_client()
            return client.has_collection(collection_name)
        except Exception as e:
            logger.error(f"Failed to check collection: {e}")
            return False
    
    def create_collection(
        self,
        collection_name: str,
        dimension: int = 1024,
        description: str = "",
        metric_type: str = "COSINE",
    ) -> CollectionInfo:
        """创建新的 collection.
        
        Args:
            collection_name: collection 名称
            dimension: 向量维度
            description: 描述
            metric_type: 距离度量类型 (COSINE, L2, IP)
        """
        try:
            client = self._get_client()
            
            if client.has_collection(collection_name):
                logger.info(f"Collection {collection_name} already exists")
                return self.get_collection_info(collection_name)
            
            client.create_collection(
                collection_name=collection_name,
                dimension=dimension,
            )
            
            # 等待创建完成
            time.sleep(0.5)
            
            logger.info(f"Created collection: {collection_name}")
            return CollectionInfo(
                name=collection_name,
                description=description,
                dimension=dimension,
            )
            
        except Exception as e:
            logger.error(f"Failed to create collection: {e}")
            raise RuntimeError(f"创建 collection 失败: {e}")
    
    def drop_collection(self, collection_name: str) -> bool:
        """删除 collection."""
        try:
            client = self._get_client()
            
            if not client.has_collection(collection_name):
                raise ValueError(f"Collection '{collection_name}' 不存在")
            
            client.drop_collection(collection_name)
            logger.info(f"Dropped collection: {collection_name}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to drop collection: {e}")
            raise RuntimeError(f"删除 collection 失败: {e}")
    
    def get_collection_info(self, collection_name: str) -> CollectionInfo:
        """获取 collection 信息."""
        try:
            client = self._get_client()
            
            if not client.has_collection(collection_name):
                raise ValueError(f"Collection '{collection_name}' 不存在")
            
            # 获取统计信息
            stats = client.get_collection_stats(collection_name)
            
            return CollectionInfo(
                name=collection_name,
                num_entities=stats.get("row_count", 0),
            )
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get collection info: {e}")
            raise RuntimeError(f"获取 collection 信息失败: {e}")
    
    def get_all_collections_info(self) -> List[Dict[str, Any]]:
        """获取所有 collections 的信息."""
        result = []
        for name in self.list_collections():
            try:
                info = self.get_collection_info(name)
                result.append({
                    "name": info.name,
                    "description": info.description,
                    "num_entities": info.num_entities,
                    "dimension": info.dimension,
                })
            except Exception as e:
                result.append({"name": name, "error": str(e)})
        return result
    
    # =========================================================================
    # 向量操作
    # =========================================================================
    
    def insert(
        self,
        collection_name: str,
        data: List[Dict[str, Any]],
    ) -> List[str]:
        """插入数据到 collection.
        
        Args:
            collection_name: collection 名称
            data: 数据列表，每个元素包含 id, vector, 以及其他字段
            
        Returns:
            插入的 ID 列表
        """
        try:
            client = self._get_client()
            
            result = client.insert(
                collection_name=collection_name,
                data=data,
            )
            
            logger.info(f"Inserted {len(data)} records to {collection_name}")
            return result.get("ids", [])
            
        except Exception as e:
            logger.error(f"Failed to insert data: {e}")
            raise RuntimeError(f"插入数据失败: {e}")
    
    def search(
        self,
        collection_name: str,
        query_vectors: List[List[float]],
        limit: int = 10,
        output_fields: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> List[List[SearchResult]]:
        """搜索相似向量.
        
        Args:
            collection_name: collection 名称
            query_vectors: 查询向量列表
            limit: 返回结果数量
            output_fields: 需要返回的字段
            filter_expr: 过滤表达式
            
        Returns:
            搜索结果列表
        """
        try:
            client = self._get_client()
            
            results = client.search(
                collection_name=collection_name,
                data=query_vectors,
                limit=limit,
                output_fields=output_fields,
                filter=filter_expr,
            )
            
            # 转换结果格式
            formatted_results = []
            for batch in results:
                batch_results = []
                for hit in batch:
                    batch_results.append(SearchResult(
                        id=str(hit.get("id", "")),
                        score=hit.get("distance", 0.0),
                        text=hit.get("text"),
                        metadata=hit.get("entity", {}),
                    ))
                formatted_results.append(batch_results)
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Failed to search: {e}")
            raise RuntimeError(f"搜索失败: {e}")
    
    def query(
        self,
        collection_name: str,
        filter_expr: str = "",
        output_fields: Optional[List[str]] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """查询数据.
        
        Args:
            collection_name: collection 名称
            filter_expr: 过滤表达式
            output_fields: 需要返回的字段
            limit: 返回结果数量
        """
        try:
            client = self._get_client()
            
            results = client.query(
                collection_name=collection_name,
                filter=filter_expr,
                output_fields=output_fields or ["*"],
                limit=limit,
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to query: {e}")
            raise RuntimeError(f"查询失败: {e}")
    
    def delete(
        self,
        collection_name: str,
        ids: Optional[List[str]] = None,
        filter_expr: Optional[str] = None,
    ) -> int:
        """删除数据.
        
        Args:
            collection_name: collection 名称
            ids: 要删除的 ID 列表
            filter_expr: 过滤表达式
            
        Returns:
            删除的记录数
        """
        try:
            client = self._get_client()
            
            if ids:
                result = client.delete(
                    collection_name=collection_name,
                    ids=ids,
                )
            elif filter_expr:
                result = client.delete(
                    collection_name=collection_name,
                    filter=filter_expr,
                )
            else:
                raise ValueError("必须提供 ids 或 filter_expr")
            
            logger.info(f"Deleted records from {collection_name}")
            return result.get("delete_count", 0)
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete: {e}")
            raise RuntimeError(f"删除失败: {e}")
    
    # =========================================================================
    # 健康检查
    # =========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查."""
        try:
            collections = self.list_collections()
            return {
                "status": "healthy",
                "uri": self.uri,
                "collections_count": len(collections),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "uri": self.uri,
                "error": str(e),
            }
