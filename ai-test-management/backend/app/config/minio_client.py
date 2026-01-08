"""
MinIO 对象存储客户端

管理 MinIO 的连接和操作
"""



import io
from typing import Optional, BinaryIO
from datetime import timedelta
# pragma: no cover  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y21oek5RPT06ZWRiOWY5MTk=

from minio import Minio
from minio.error import S3Error

from app.config.settings import settings


class MinIOClient:
    """MinIO 客户端管理器"""
    
    _client: Optional[Minio] = None
    _bucket_ensured: bool = False
    
    @classmethod
    def get_client(cls) -> Minio:
        """获取 MinIO 客户端实例"""
        if cls._client is None:
            cls._client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
                region=settings.minio_region,
            )
        return cls._client
    
    @classmethod
    def ensure_bucket(cls) -> None:
        """确保存储桶存在"""
        if cls._bucket_ensured:
            return
        
        client = cls.get_client()
        bucket_name = settings.minio_bucket
        
        try:
            if not client.bucket_exists(bucket_name):
                client.make_bucket(bucket_name)
        except S3Error as e:
            # 桶已存在，忽略错误
            if e.code != "BucketAlreadyOwnedByYou":
                raise
        
        cls._bucket_ensured = True
    
    @classmethod
    def upload_file(
        cls,
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传文件到 MinIO
        
        Args:
            object_name: 对象名称（存储路径）
            data: 文件数据流
            length: 文件长度
            content_type: 内容类型
            
        Returns:
            str: 对象名称
        """
        cls.ensure_bucket()
        client = cls.get_client()
# fmt: off  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y21oek5RPT06ZWRiOWY5MTk=
        
        client.put_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            data=data,
            length=length,
            content_type=content_type,
        )
        
        return object_name
    
    @classmethod
    def upload_bytes(
        cls,
        object_name: str,
        data: bytes,
        content_type: str = "application/octet-stream",
    ) -> str:
        """
        上传字节数据到 MinIO
        
        Args:
            object_name: 对象名称
            data: 字节数据
            content_type: 内容类型
            
        Returns:
            str: 对象名称
        """
        return cls.upload_file(
            object_name=object_name,
            data=io.BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
    
    @classmethod
    def download_file(cls, object_name: str) -> bytes:
        """
        从 MinIO 下载文件
        
        Args:
            object_name: 对象名称
            
        Returns:
            bytes: 文件内容
        """
        client = cls.get_client()
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y21oek5RPT06ZWRiOWY5MTk=
        
        response = client.get_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
        )
        
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()
    
    @classmethod
    def get_presigned_url(
        cls,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
    ) -> str:
        """
        获取预签名 URL（用于下载）
        
        Args:
            object_name: 对象名称
            expires: 过期时间
            
        Returns:
            str: 预签名 URL
        """
        client = cls.get_client()
        
        return client.presigned_get_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
            expires=expires,
        )
    
    @classmethod
    def delete_file(cls, object_name: str) -> None:
        """
        从 MinIO 删除文件
        
        Args:
            object_name: 对象名称
        """
        client = cls.get_client()
        
        client.remove_object(
            bucket_name=settings.minio_bucket,
            object_name=object_name,
        )
# pylint: disable  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y21oek5RPT06ZWRiOWY5MTk=
    
    @classmethod
    def file_exists(cls, object_name: str) -> bool:
        """
        检查文件是否存在
        
        Args:
            object_name: 对象名称
            
        Returns:
            bool: 是否存在
        """
        client = cls.get_client()
        
        try:
            client.stat_object(
                bucket_name=settings.minio_bucket,
                object_name=object_name,
            )
            return True
        except S3Error as e:
            if e.code == "NoSuchKey":
                return False
            raise

