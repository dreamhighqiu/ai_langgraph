"""
LightRAG HTTP 客户端
通过 HTTP API 与 anything-chat-rag 服务通信
使用 LIGHTRAG-WORKSPACE header 实现 Collection 隔离
"""
import httpx
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)


class LightRAGClient:
    """LightRAG HTTP 客户端"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout: float = 300.0):
        """
        初始化客户端
        
        Args:
            base_url: LightRAG 服务地址 (例如: http://localhost:9621)
            api_key: API Key (可选)
            timeout: 超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
        logger.info(f'LightRAG 客户端初始化: {self.base_url}')
    
    def _get_headers(self, workspace: str) -> Dict[str, str]:
        """
        获取请求头
        
        Args:
            workspace: 工作空间名称（对应 Milvus Collection 前缀）
        
        Returns:
            请求头字典
        """
        headers = {
            'LIGHTRAG-WORKSPACE': workspace
        }
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        return headers
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            response = await self.client.get(f'{self.base_url}/health')
            response.raise_for_status()
            return {'status': 'ok', 'data': response.json()}
        except Exception as e:
            logger.error(f'LightRAG 健康检查失败: {e}')
            return {'status': 'error', 'message': str(e)}
    
    async def upload_document(
        self,
        workspace: str,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文档到 LightRAG
        
        Args:
            workspace: 工作空间（Collection 前缀）
            file_content: 文件内容
            filename: 文件名
            metadata: 元数据
        
        Returns:
            上传结果
        """
        try:
            headers = self._get_headers(workspace)
            files = {'file': (filename, file_content, 'application/octet-stream')}
            data = {}
            if metadata:
                data['metadata'] = str(metadata)
            
            response = await self.client.post(
                f'{self.base_url}/documents/upload',
                headers=headers,
                files=files,
                data=data
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f'文档上传成功: {filename} (workspace: {workspace})')
            return result
        except Exception as e:
            logger.error(f'文档上传失败: {filename} (workspace: {workspace}), 错误: {e}')
            raise
    
    async def query_knowledge(
        self,
        workspace: str,
        query: str,
        mode: str = 'hybrid',
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询知识库
        
        Args:
            workspace: 工作空间
            query: 查询文本
            mode: 查询模式 (naive/local/global/hybrid)
            top_k: 返回结果数量
        
        Returns:
            查询结果
        """
        try:
            headers = self._get_headers(workspace)
            json_data = {
                'query': query,
                'mode': mode
            }
            if top_k:
                json_data['top_k'] = top_k
            
            response = await self.client.post(
                f'{self.base_url}/query',
                headers=headers,
                json=json_data
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f'查询成功: {query[:50]}... (workspace: {workspace})')
            return result
        except Exception as e:
            logger.error(f'查询失败: {query[:50]}... (workspace: {workspace}), 错误: {e}')
            raise
    
    async def delete_document(self, workspace: str, doc_id: str) -> Dict[str, Any]:
        """
        删除文档
        
        Args:
            workspace: 工作空间
            doc_id: 文档ID
        
        Returns:
            删除结果
        """
        try:
            headers = self._get_headers(workspace)
            response = await self.client.delete(
                f'{self.base_url}/documents/{doc_id}',
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f'文档删除成功: {doc_id} (workspace: {workspace})')
            return result
        except Exception as e:
            logger.error(f'文档删除失败: {doc_id} (workspace: {workspace}), 错误: {e}')
            raise
    
    async def delete_workspace(self, workspace: str) -> Dict[str, Any]:
        """
        删除工作空间（删除所有文档）
        
        Args:
            workspace: 工作空间
        
        Returns:
            删除结果
        """
        try:
            headers = self._get_headers(workspace)
            response = await self.client.delete(
                f'{self.base_url}/documents/delete_all',
                headers=headers
            )
            response.raise_for_status()
            result = response.json()
            logger.info(f'工作空间清空成功: {workspace}')
            return result
        except Exception as e:
            logger.error(f'工作空间清空失败: {workspace}, 错误: {e}')
            raise
    
    async def get_document_status(self, workspace: str, doc_id: str) -> Dict[str, Any]:
        """
        获取文档状态
        
        Args:
            workspace: 工作空间
            doc_id: 文档ID
        
        Returns:
            文档状态
        """
        try:
            headers = self._get_headers(workspace)
            response = await self.client.get(
                f'{self.base_url}/documents/{doc_id}/status',
                headers=headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f'获取文档状态失败: {doc_id} (workspace: {workspace}), 错误: {e}')
            raise
    
    async def get_documents_paginated(
        self,
        workspace: str,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_field: str = 'updated_at',
        sort_direction: str = 'desc'
    ) -> Dict[str, Any]:
        """
        获取分页文档列表（RAG处理后的文档）
        
        Args:
            workspace: 工作空间名称
            status_filter: 状态过滤（PENDING/PROCESSING/PREPROCESSED/PROCESSED/FAILED）
            page: 页码（从1开始）
            page_size: 每页数量（10-200）
            sort_field: 排序字段（created_at/updated_at/id/file_path）
            sort_direction: 排序方向（asc/desc）
        
        Returns:
            分页文档列表
        """
        try:
            headers = self._get_headers(workspace)
            payload = {
                'page': page,
                'page_size': page_size,
                'sort_field': sort_field,
                'sort_direction': sort_direction
            }
            if status_filter:
                payload['status_filter'] = status_filter
            
            response = await self.client.post(
                f'{self.base_url}/documents/paginated',
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            logger.debug(f'获取文档列表成功: workspace={workspace}, page={page}, total={result.get("total", 0)}')
            return result
        except Exception as e:
            logger.error(f'获取文档列表失败: workspace={workspace}, 错误: {e}')
            raise
    
    async def init_workspace(self, workspace: str) -> Dict[str, Any]:
        """
        初始化工作空间（通过上传占位文档来触发 Milvus 集合创建）
        
        Args:
            workspace: 工作空间名称（对应 Milvus Collection 前缀）
        
        Returns:
            初始化结果
        """
        try:
            # 创建一个最小的占位文档来触发集合创建
            placeholder_content = b"# Knowledge Base Initialization\n\nThis is a placeholder document to initialize the workspace."
            placeholder_filename = ".init_placeholder.md"
            
            result = await self.upload_document(
                workspace=workspace,
                file_content=placeholder_content,
                filename=placeholder_filename,
                metadata={'type': 'init_placeholder', 'auto_created': True}
            )
            
            logger.info(f'工作空间初始化成功: {workspace}')
            return {'status': 'ok', 'workspace': workspace, 'message': 'Workspace initialized successfully'}
        except Exception as e:
            logger.error(f'工作空间初始化失败: {workspace}, 错误: {e}')
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


class LightRAGManager:
    """LightRAG 管理器（单例）"""
    
    _instance: Optional[LightRAGClient] = None
    _base_url: str = None
    _api_key: Optional[str] = None
    
    @classmethod
    def configure(cls, base_url: str = None, api_key: Optional[str] = None):
        """
        配置 LightRAG 客户端
        
        Args:
            base_url: LightRAG 服务地址
            api_key: API Key
        """
        if base_url:
            cls._base_url = base_url
        if api_key:
            cls._api_key = api_key
        
        # 从环境变量读取配置
        if not cls._base_url:
            cls._base_url = os.getenv('LIGHTRAG_BASE_URL', 'http://localhost:9621')
        if not cls._api_key:
            cls._api_key = os.getenv('LIGHTRAG_API_KEY')
        
        logger.info(f'LightRAG 管理器配置完成: {cls._base_url}')
    
    @classmethod
    def get_client(cls) -> LightRAGClient:
        """获取客户端实例（单例）"""
        if cls._instance is None:
            if cls._base_url is None:
                cls.configure()
            cls._instance = LightRAGClient(cls._base_url, cls._api_key)
        return cls._instance
    
    @classmethod
    async def upload_document(
        cls,
        collection_name: str,
        file_content: bytes,
        filename: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        上传文档
        
        Args:
            collection_name: Collection 名称（作为 workspace）
            file_content: 文件内容
            filename: 文件名
            metadata: 元数据
        
        Returns:
            上传结果
        """
        client = cls.get_client()
        return await client.upload_document(collection_name, file_content, filename, metadata)
    
    @classmethod
    async def query_knowledge(
        cls,
        collection_name: str,
        query: str,
        mode: str = 'hybrid',
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        查询知识库
        
        Args:
            collection_name: Collection 名称
            query: 查询文本
            mode: 查询模式
            top_k: 返回结果数量
        
        Returns:
            查询结果
        """
        client = cls.get_client()
        return await client.query_knowledge(collection_name, query, mode, top_k)
    
    @classmethod
    async def delete_workspace(cls, collection_name: str) -> Dict[str, Any]:
        """
        删除工作空间
        
        Args:
            collection_name: Collection 名称
        
        Returns:
            删除结果
        """
        client = cls.get_client()
        return await client.delete_workspace(collection_name)
    
    @classmethod
    async def health_check(cls) -> Dict[str, Any]:
        """健康检查"""
        client = cls.get_client()
        return await client.health_check()
    
    @classmethod
    async def init_workspace(cls, collection_name: str) -> Dict[str, Any]:
        """
        初始化工作空间（创建 Milvus 集合）
        
        Args:
            collection_name: Collection 名称（作为 workspace）
        
        Returns:
            初始化结果
        """
        client = cls.get_client()
        return await client.init_workspace(collection_name)
    
    @classmethod
    async def get_documents_paginated(
        cls,
        collection_name: str,
        status_filter: Optional[str] = None,
        page: int = 1,
        page_size: int = 50,
        sort_field: str = 'updated_at',
        sort_direction: str = 'desc'
    ) -> Dict[str, Any]:
        """
        获取分页文档列表（RAG处理后的文档）
        
        Args:
            collection_name: Collection 名称（作为 workspace）
            status_filter: 状态过滤
            page: 页码
            page_size: 每页数量
            sort_field: 排序字段
            sort_direction: 排序方向
        
        Returns:
            分页文档列表
        """
        client = cls.get_client()
        return await client.get_documents_paginated(
            collection_name,
            status_filter,
            page,
            page_size,
            sort_field,
            sort_direction
        )


def get_lightrag_manager() -> type[LightRAGManager]:
    """获取 LightRAG 管理器"""
    return LightRAGManager


