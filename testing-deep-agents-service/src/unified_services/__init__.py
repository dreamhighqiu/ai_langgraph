"""统一服务层 - 整合所有存储和数据服务.

这个模块提供统一的服务接口，整合：
1. Milvus 向量数据库操作
2. MinIO 对象存储操作
3. 知识库管理（LightRAG 集成）
4. 数据库操作（Tortoise ORM）

所有服务都可以：
- 被 FastAPI 路由直接调用
- 被封装为 LangChain 工具供智能体使用
- 被多个前端应用共享（testing-deep-agents-ui, autogen_study/web）

使用示例：
    # 单例模式
    milvus = MilvusService.get_instance()
    minio = MinIOService.get_instance()
    knowledge = KnowledgeService.get_instance()
    database = DatabaseService.get_instance()
    
    # 或者实例模式
    milvus = MilvusService(uri="http://localhost:19530")
"""

from unified_services.milvus_service import MilvusService, CollectionInfo, SearchResult
from unified_services.minio_service import MinIOService, BucketInfo, ObjectInfo
from unified_services.knowledge_service import (
    KnowledgeService,
    KnowledgeBase,
    Document,
    QueryResult,
    QueryMode,
    UploadMode,
)
from unified_services.database_service import DatabaseService, DatabaseConfig
from unified_services.tools import (
    knowledge_tools,
    milvus_tools,
    minio_tools,
    all_tools,
)

__all__ = [
    # Milvus
    "MilvusService",
    "CollectionInfo",
    "SearchResult",
    # MinIO
    "MinIOService",
    "BucketInfo",
    "ObjectInfo",
    # Knowledge
    "KnowledgeService",
    "KnowledgeBase",
    "Document",
    "QueryResult",
    "QueryMode",
    "UploadMode",
    # Database
    "DatabaseService",
    "DatabaseConfig",
    # LangChain Tools
    "knowledge_tools",
    "milvus_tools",
    "minio_tools",
    "all_tools",
]
