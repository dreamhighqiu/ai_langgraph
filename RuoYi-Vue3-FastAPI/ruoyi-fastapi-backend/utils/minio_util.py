"""
MinIO对象存储工具类
"""
from typing import Optional
from io import BytesIO
from minio import Minio
from minio.error import S3Error
from datetime import timedelta

from config.env import MinIOConfig
from utils.log_util import logger


class MinioUtil:
    """MinIO工具类"""

    def __init__(self):
        """初始化MinIO客户端"""
        try:
            self.client = Minio(
                endpoint=MinIOConfig.minio_endpoint or "localhost:9000",
                access_key=MinIOConfig.minio_access_key or "minioadmin",
                secret_key=MinIOConfig.minio_secret_key or "minioadmin",
                secure=MinIOConfig.minio_secure or False
            )
            logger.info("MinIO客户端初始化成功")
        except Exception as e:
            logger.error(f"MinIO客户端初始化失败: {str(e)}")
            raise

    def create_bucket(self, bucket_name: str) -> bool:
        """创建存储桶"""
        try:
            if not self.client.bucket_exists(bucket_name):
                self.client.make_bucket(bucket_name)
                logger.info(f"创建存储桶成功: {bucket_name}")
            return True
        except S3Error as e:
            logger.error(f"创建存储桶失败: {str(e)}")
            return False

    async def upload_file(
        self,
        bucket_name: str,
        object_name: str,
        file_content: bytes,
        content_type: str = "application/octet-stream"
    ) -> str:
        """
        上传文件到MinIO
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称(文件路径)
            file_content: 文件内容
            content_type: 内容类型
        
        Returns:
            文件访问URL
        """
        try:
            # 确保存储桶存在
            self.create_bucket(bucket_name)
            
            # 上传文件
            file_stream = BytesIO(file_content)
            self.client.put_object(
                bucket_name=bucket_name,
                object_name=object_name,
                data=file_stream,
                length=len(file_content),
                content_type=content_type
            )
            
            # 生成访问URL
            url = self.get_presigned_url(bucket_name, object_name)
            logger.info(f"文件上传成功: {object_name}")
            return url
            
        except S3Error as e:
            logger.error(f"文件上传失败: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"文件上传异常: {str(e)}")
            raise

    def get_presigned_url(
        self,
        bucket_name: str,
        object_name: str,
        expires: int = 7 * 24 * 3600  # 7天
    ) -> str:
        """
        获取预签名URL
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
            expires: 过期时间(秒)
        
        Returns:
            预签名URL
        """
        try:
            url = self.client.presigned_get_object(
                bucket_name=bucket_name,
                object_name=object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"获取预签名URL失败: {str(e)}")
            raise

    async def download_file(
        self,
        bucket_name: str,
        object_name: str
    ) -> bytes:
        """
        从MinIO下载文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
        
        Returns:
            文件内容
        """
        try:
            response = self.client.get_object(bucket_name, object_name)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error as e:
            logger.error(f"文件下载失败: {str(e)}")
            raise

    def delete_file(
        self,
        bucket_name: str,
        object_name: str
    ) -> bool:
        """
        删除文件
        
        Args:
            bucket_name: 存储桶名称
            object_name: 对象名称
        
        Returns:
            是否成功
        """
        try:
            self.client.remove_object(bucket_name, object_name)
            logger.info(f"文件删除成功: {object_name}")
            return True
        except S3Error as e:
            logger.error(f"文件删除失败: {str(e)}")
            return False

    def list_objects(
        self,
        bucket_name: str,
        prefix: Optional[str] = None
    ) -> list:
        """
        列出对象
        
        Args:
            bucket_name: 存储桶名称
            prefix: 前缀过滤
        
        Returns:
            对象列表
        """
        try:
            objects = self.client.list_objects(bucket_name, prefix=prefix, recursive=True)
            return [obj.object_name for obj in objects]
        except S3Error as e:
            logger.error(f"列出对象失败: {str(e)}")
            return []

