"""MinIO 对象存储服务.

整合 MinIO 的所有操作，提供统一的接口：
- Bucket 管理（创建、删除、列表）
- 文件操作（上传、下载、删除、列表）
- URL 生成（预签名 URL、永久代理 URL）
"""

import os
import io
import uuid
import logging
from typing import Optional, List, Dict, Any, BinaryIO
from dataclasses import dataclass
from datetime import datetime, timedelta
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
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_DEFAULT_BUCKET = os.getenv("MINIO_DEFAULT_BUCKET", "knowledge-base")


@dataclass
class BucketInfo:
    """Bucket 信息."""
    name: str
    created_at: Optional[datetime] = None


@dataclass
class ObjectInfo:
    """对象信息."""
    name: str
    size: int
    content_type: Optional[str] = None
    last_modified: Optional[datetime] = None
    etag: Optional[str] = None
    is_dir: bool = False


class MinIOService:
    """MinIO 对象存储服务.
    
    提供两种使用模式：
    1. 单例模式：MinIOService.get_instance()
    2. 实例模式：MinIOService(endpoint=...)
    """
    
    _instance: Optional["MinIOService"] = None
    
    @classmethod
    def get_instance(cls) -> "MinIOService":
        """获取单例实例."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(
        self,
        endpoint: str = MINIO_ENDPOINT,
        access_key: str = MINIO_ACCESS_KEY,
        secret_key: str = MINIO_SECRET_KEY,
        secure: bool = MINIO_SECURE,
        default_bucket: str = MINIO_DEFAULT_BUCKET,
        lazy_init: bool = True,
    ):
        """初始化 MinIO 服务.
        
        Args:
            endpoint: MinIO 服务地址
            access_key: 访问密钥
            secret_key: 秘密密钥
            secure: 是否使用 HTTPS
            default_bucket: 默认 bucket
            lazy_init: 是否延迟初始化（不立即检查连接）
        """
        self.endpoint = endpoint
        self.access_key = access_key
        self.secret_key = secret_key
        self.secure = secure
        self.default_bucket = default_bucket
        self._client = None
        
        if not lazy_init:
            self._get_client()
            self._ensure_default_bucket()
    
    def _get_client(self):
        """获取 MinIO 客户端."""
        if self._client is None:
            try:
                from minio import Minio
                self._client = Minio(
                    endpoint=self.endpoint,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.secure,
                )
                logger.info(f"Connected to MinIO at {self.endpoint}")
            except Exception as e:
                logger.error(f"Failed to connect to MinIO: {e}")
                raise ConnectionError(f"无法连接到 MinIO: {e}")
        return self._client
    
    def _ensure_default_bucket(self):
        """确保默认 bucket 存在."""
        try:
            client = self._get_client()
            if not client.bucket_exists(self.default_bucket):
                client.make_bucket(self.default_bucket)
                logger.info(f"Created default bucket: {self.default_bucket}")
        except Exception as e:
            logger.warning(f"Could not ensure default bucket: {e}")
    
    # =========================================================================
    # Bucket 管理
    # =========================================================================
    
    def list_buckets(self) -> List[BucketInfo]:
        """列出所有 buckets."""
        try:
            client = self._get_client()
            buckets = client.list_buckets()
            return [
                BucketInfo(name=b.name, created_at=b.creation_date)
                for b in buckets
            ]
        except Exception as e:
            logger.error(f"Failed to list buckets: {e}")
            raise RuntimeError(f"列出 buckets 失败: {e}")
    
    def bucket_exists(self, bucket_name: str) -> bool:
        """检查 bucket 是否存在."""
        try:
            client = self._get_client()
            return client.bucket_exists(bucket_name)
        except Exception as e:
            logger.error(f"Failed to check bucket: {e}")
            return False
    
    def create_bucket(self, bucket_name: str) -> BucketInfo:
        """创建 bucket."""
        try:
            client = self._get_client()
            
            if client.bucket_exists(bucket_name):
                raise ValueError(f"Bucket '{bucket_name}' 已存在")
            
            client.make_bucket(bucket_name)
            logger.info(f"Created bucket: {bucket_name}")
            return BucketInfo(name=bucket_name, created_at=datetime.now())
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")
            raise RuntimeError(f"创建 bucket 失败: {e}")
    
    def delete_bucket(self, bucket_name: str, force: bool = False) -> bool:
        """删除 bucket.
        
        Args:
            bucket_name: bucket 名称
            force: 是否强制删除（包括其中的所有文件）
        """
        try:
            client = self._get_client()
            
            if not client.bucket_exists(bucket_name):
                raise ValueError(f"Bucket '{bucket_name}' 不存在")
            
            if force:
                # 删除所有对象
                objects = client.list_objects(bucket_name, recursive=True)
                for obj in objects:
                    client.remove_object(bucket_name, obj.object_name)
            
            client.remove_bucket(bucket_name)
            logger.info(f"Deleted bucket: {bucket_name}")
            return True
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to delete bucket: {e}")
            raise RuntimeError(f"删除 bucket 失败: {e}")
    
    # =========================================================================
    # 文件操作
    # =========================================================================
    
    def list_objects(
        self,
        bucket_name: Optional[str] = None,
        prefix: str = "",
        recursive: bool = False,
    ) -> List[ObjectInfo]:
        """列出 bucket 中的对象."""
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            if not client.bucket_exists(bucket):
                raise ValueError(f"Bucket '{bucket}' 不存在")
            
            objects = client.list_objects(bucket, prefix=prefix, recursive=recursive)
            
            return [
                ObjectInfo(
                    name=obj.object_name,
                    size=obj.size or 0,
                    content_type=obj.content_type,
                    last_modified=obj.last_modified,
                    etag=obj.etag,
                    is_dir=obj.is_dir,
                )
                for obj in objects
            ]
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to list objects: {e}")
            raise RuntimeError(f"列出对象失败: {e}")
    
    async def upload_file(
        self,
        file_data: BinaryIO,
        filename: str,
        bucket_name: Optional[str] = None,
        object_name: Optional[str] = None,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None,
    ) -> ObjectInfo:
        """上传文件.
        
        Args:
            file_data: 文件数据流
            filename: 原始文件名
            bucket_name: bucket 名称
            object_name: 对象名称（如果不指定，自动生成）
            content_type: 内容类型
            metadata: 元数据
        """
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            # 确保 bucket 存在
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
            
            # 生成唯一对象名
            if not object_name:
                ext = os.path.splitext(filename)[1]
                object_name = f"{uuid.uuid4().hex}{ext}"
            
            # 获取文件大小
            file_data.seek(0, 2)
            file_size = file_data.tell()
            file_data.seek(0)
            
            # 处理文本文件的编码
            if content_type.startswith("text/") or filename.lower().endswith(
                ('.txt', '.md', '.json', '.xml', '.html', '.css', '.js')
            ):
                if 'charset=' not in content_type:
                    content_type = f"{content_type}; charset=utf-8"
            
            # 上传
            result = client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type,
                metadata=metadata,
            )
            
            logger.info(f"Uploaded file: {bucket}/{object_name}, size: {file_size}")
            
            return ObjectInfo(
                name=object_name,
                size=file_size,
                content_type=content_type,
                etag=result.etag,
            )
            
        except Exception as e:
            logger.error(f"Failed to upload file: {e}")
            raise RuntimeError(f"上传文件失败: {e}")
    
    def upload_bytes(
        self,
        data: bytes,
        filename: str,
        bucket_name: Optional[str] = None,
        object_name: Optional[str] = None,
        content_type: str = "application/octet-stream",
    ) -> ObjectInfo:
        """上传字节数据（同步版本）."""
        import asyncio
        return asyncio.get_event_loop().run_until_complete(
            self.upload_file(
                io.BytesIO(data),
                filename,
                bucket_name,
                object_name,
                content_type,
            )
        )
    
    async def download_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> bytes:
        """下载文件内容."""
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            response = client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            
            logger.info(f"Downloaded file: {bucket}/{object_name}")
            return data
            
        except Exception as e:
            logger.error(f"Failed to download file: {e}")
            raise RuntimeError(f"下载文件失败: {e}")
    
    def delete_object(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
    ) -> bool:
        """删除对象."""
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            client.remove_object(bucket, object_name)
            logger.info(f"Deleted object: {bucket}/{object_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete object: {e}")
            raise RuntimeError(f"删除对象失败: {e}")
    
    def delete_objects(
        self,
        object_names: List[str],
        bucket_name: Optional[str] = None,
    ) -> List[str]:
        """批量删除对象."""
        try:
            from minio.deleteobjects import DeleteObject
            
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            delete_objects = [DeleteObject(name) for name in object_names]
            errors = client.remove_objects(bucket, delete_objects)
            
            error_names = set()
            for error in errors:
                logger.warning(f"Failed to delete {error.name}: {error.message}")
                error_names.add(error.name)
            
            deleted = [name for name in object_names if name not in error_names]
            logger.info(f"Deleted {len(deleted)} objects from {bucket}")
            return deleted
            
        except Exception as e:
            logger.error(f"Failed to delete objects: {e}")
            raise RuntimeError(f"批量删除对象失败: {e}")
    
    # =========================================================================
    # URL 生成
    # =========================================================================
    
    def get_presigned_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        expires_hours: int = 24,
    ) -> str:
        """获取预签名 URL."""
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            url = client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(hours=expires_hours),
            )
            return url
            
        except Exception as e:
            logger.error(f"Failed to get presigned URL: {e}")
            raise RuntimeError(f"获取预签名 URL 失败: {e}")
    
    def get_proxy_url(
        self,
        object_name: str,
        bucket_name: Optional[str] = None,
        api_prefix: str = "/api/v1/files/proxy",
    ) -> str:
        """获取代理 URL（永久有效）."""
        bucket = bucket_name or self.default_bucket
        return f"{api_prefix}/{bucket}/{object_name}"
    
    # =========================================================================
    # 统计信息
    # =========================================================================
    
    def get_bucket_stats(self, bucket_name: Optional[str] = None) -> Dict[str, Any]:
        """获取 bucket 统计信息."""
        try:
            client = self._get_client()
            bucket = bucket_name or self.default_bucket
            
            if not client.bucket_exists(bucket):
                raise ValueError(f"Bucket '{bucket}' 不存在")
            
            objects = list(client.list_objects(bucket, recursive=True))
            
            total_size = sum(obj.size or 0 for obj in objects)
            file_count = len(objects)
            
            # 按扩展名统计
            extensions: Dict[str, Dict[str, int]] = {}
            for obj in objects:
                if not obj.is_dir:
                    ext = os.path.splitext(obj.object_name)[1].lower() or ".unknown"
                    if ext not in extensions:
                        extensions[ext] = {"count": 0, "size": 0}
                    extensions[ext]["count"] += 1
                    extensions[ext]["size"] += obj.size or 0
            
            return {
                "name": bucket,
                "total_size": total_size,
                "total_size_human": self._format_size(total_size),
                "file_count": file_count,
                "extensions": extensions,
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Failed to get bucket stats: {e}")
            raise RuntimeError(f"获取 bucket 统计信息失败: {e}")
    
    @staticmethod
    def _format_size(size: int) -> str:
        """格式化文件大小."""
        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} PB"
    
    # =========================================================================
    # 健康检查
    # =========================================================================
    
    def health_check(self) -> Dict[str, Any]:
        """健康检查."""
        try:
            buckets = self.list_buckets()
            return {
                "status": "healthy",
                "endpoint": self.endpoint,
                "buckets_count": len(buckets),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "endpoint": self.endpoint,
                "error": str(e),
            }
