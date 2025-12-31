"""
MinIO对象存储客户端
用于存储测试脚本、报告等文件
"""
import io
import os
from datetime import timedelta
from typing import Optional, Tuple

from config.env import MinIOConfig, StorageConfig
from utils.log_util import logger

try:
    from minio import Minio
    from minio.error import S3Error
    MINIO_AVAILABLE = True
except ImportError:
    MINIO_AVAILABLE = False
    logger.warning("minio库未安装，将使用本地存储模式")


class MinIOClient:
    """MinIO客户端封装"""
    
    def __init__(
        self,
        endpoint: str = None,
        access_key: str = None,
        secret_key: str = None,
        bucket_name: str = None,
        secure: bool = None
    ):
        """
        初始化MinIO客户端
        
        Args:
            endpoint: MinIO服务地址，如 localhost:9000
            access_key: 访问密钥
            secret_key: 密钥
            bucket_name: 默认存储桶名称
            secure: 是否使用HTTPS
        """
        # 优先使用参数，否则使用配置中心
        self.endpoint = endpoint or MinIOConfig.minio_endpoint
        self.access_key = access_key or MinIOConfig.minio_access_key
        self.secret_key = secret_key or MinIOConfig.minio_secret_key
        self.bucket_name = bucket_name or MinIOConfig.minio_bucket
        self.secure = secure if secure is not None else MinIOConfig.minio_secure
        
        self.client = None
        self.use_local = not MINIO_AVAILABLE
        self.local_storage_path = StorageConfig.local_storage_path
        
        if MINIO_AVAILABLE:
            try:
                self.client = Minio(
                    self.endpoint,
                    access_key=self.access_key,
                    secret_key=self.secret_key,
                    secure=self.secure
                )
                # 确保bucket存在
                self._ensure_bucket()
                logger.info(f"MinIO客户端初始化成功: {self.endpoint}")
            except Exception as e:
                logger.warning(f"MinIO连接失败，使用本地存储: {e}")
                self.use_local = True
    
    def _ensure_bucket(self):
        """确保存储桶存在"""
        if self.client:
            try:
                if not self.client.bucket_exists(self.bucket_name):
                    self.client.make_bucket(self.bucket_name)
                    logger.info(f"创建存储桶: {self.bucket_name}")
            except S3Error as e:
                logger.error(f"创建存储桶失败: {e}")
    
    def _get_local_path(self, object_name: str) -> str:
        """获取本地存储路径"""
        path = os.path.join(self.local_storage_path, self.bucket_name, object_name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        return path
    
    def upload_file(
        self,
        file_content: bytes,
        object_name: str,
        content_type: str = 'application/octet-stream'
    ) -> Tuple[bool, str]:
        """
        上传文件
        
        Args:
            file_content: 文件内容（字节）
            object_name: 对象名称/路径
            content_type: 内容类型
            
        Returns:
            (成功标志, 存储路径或错误信息)
        """
        try:
            if self.use_local:
                # 本地存储
                local_path = self._get_local_path(object_name)
                with open(local_path, 'wb') as f:
                    f.write(file_content)
                path = f"local://{self.bucket_name}/{object_name}"
                logger.debug(f"文件已保存到本地: {local_path}")
            else:
                # MinIO存储
                self.client.put_object(
                    self.bucket_name,
                    object_name,
                    io.BytesIO(file_content),
                    length=len(file_content),
                    content_type=content_type
                )
                path = f"minio://{self.bucket_name}/{object_name}"
                logger.debug(f"文件已上传到MinIO: {object_name}")
            
            return True, path
            
        except Exception as e:
            logger.error(f"上传文件失败: {e}")
            return False, str(e)
    
    def download_file(self, object_path: str) -> Tuple[bool, Optional[bytes]]:
        """
        下载文件
        
        Args:
            object_path: 对象路径 (minio://bucket/path 或 local://bucket/path)
            
        Returns:
            (成功标志, 文件内容或None)
        """
        try:
            # 解析路径
            if object_path.startswith('local://'):
                path_parts = object_path[8:].split('/', 1)
                bucket = path_parts[0]
                object_name = path_parts[1] if len(path_parts) > 1 else ''
                local_path = os.path.join(self.local_storage_path, bucket, object_name)
                
                if os.path.exists(local_path):
                    with open(local_path, 'rb') as f:
                        return True, f.read()
                return False, None
                
            elif object_path.startswith('minio://'):
                path_parts = object_path[8:].split('/', 1)
                bucket = path_parts[0]
                object_name = path_parts[1] if len(path_parts) > 1 else ''
                
                if self.use_local:
                    # 回退到本地存储
                    local_path = os.path.join(self.local_storage_path, bucket, object_name)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            return True, f.read()
                    return False, None
                
                response = self.client.get_object(bucket, object_name)
                data = response.read()
                response.close()
                response.release_conn()
                return True, data
            else:
                # 尝试作为相对路径处理
                if self.use_local:
                    local_path = self._get_local_path(object_path)
                    if os.path.exists(local_path):
                        with open(local_path, 'rb') as f:
                            return True, f.read()
                    return False, None
                else:
                    response = self.client.get_object(self.bucket_name, object_path)
                    data = response.read()
                    response.close()
                    response.release_conn()
                    return True, data
                
        except Exception as e:
            logger.error(f"下载文件失败: {e}")
            return False, None
    
    def delete_file(self, object_path: str) -> bool:
        """
        删除文件
        
        Args:
            object_path: 对象路径
            
        Returns:
            是否删除成功
        """
        try:
            if object_path.startswith('local://'):
                path_parts = object_path[8:].split('/', 1)
                bucket = path_parts[0]
                object_name = path_parts[1] if len(path_parts) > 1 else ''
                local_path = os.path.join(self.local_storage_path, bucket, object_name)
                
                if os.path.exists(local_path):
                    os.remove(local_path)
                    return True
                return False
                
            elif object_path.startswith('minio://'):
                path_parts = object_path[8:].split('/', 1)
                bucket = path_parts[0]
                object_name = path_parts[1] if len(path_parts) > 1 else ''
                
                if self.use_local:
                    local_path = os.path.join(self.local_storage_path, bucket, object_name)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                        return True
                    return False
                
                self.client.remove_object(bucket, object_name)
                return True
            else:
                if self.use_local:
                    local_path = self._get_local_path(object_path)
                    if os.path.exists(local_path):
                        os.remove(local_path)
                        return True
                    return False
                else:
                    self.client.remove_object(self.bucket_name, object_path)
                    return True
                    
        except Exception as e:
            logger.error(f"删除文件失败: {e}")
            return False
    
    def get_presigned_url(
        self,
        object_path: str,
        expires: int = 3600
    ) -> Optional[str]:
        """
        获取预签名URL
        
        Args:
            object_path: 对象路径
            expires: 过期时间（秒）
            
        Returns:
            预签名URL或None
        """
        try:
            if self.use_local or object_path.startswith('local://'):
                # 本地存储不支持预签名URL，返回直接下载API路径
                return None
            
            if object_path.startswith('minio://'):
                path_parts = object_path[8:].split('/', 1)
                bucket = path_parts[0]
                object_name = path_parts[1] if len(path_parts) > 1 else ''
            else:
                bucket = self.bucket_name
                object_name = object_path
            
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
            
        except Exception as e:
            logger.error(f"获取预签名URL失败: {e}")
            return None
    
    def list_files(self, prefix: str = '') -> list:
        """
        列出文件

        Args:
            prefix: 路径前缀

        Returns:
            文件列表
        """
        try:
            if self.use_local:
                local_dir = os.path.join(self.local_storage_path, self.bucket_name, prefix)
                files = []
                if os.path.exists(local_dir):
                    for root, _, filenames in os.walk(local_dir):
                        for filename in filenames:
                            rel_path = os.path.relpath(
                                os.path.join(root, filename),
                                os.path.join(self.local_storage_path, self.bucket_name)
                            )
                            files.append(rel_path.replace('\\', '/'))
                return files
            else:
                objects = self.client.list_objects(
                    self.bucket_name,
                    prefix=prefix,
                    recursive=True
                )
                return [obj.object_name for obj in objects]

        except Exception as e:
            logger.error(f"列出文件失败: {e}")
            return []

    # ==================== 性能测试专用方法 ====================

    async def upload_script(self, script_content: str, filename: str) -> str:
        """
        上传测试脚本

        Args:
            script_content: 脚本内容
            filename: 文件名

        Returns:
            脚本存储路径
        """
        object_name = f"scripts/{filename}"
        success, path = self.upload_file(
            file_content=script_content.encode('utf-8'),
            object_name=object_name,
            content_type='application/javascript'
        )

        if not success:
            raise Exception(f"上传脚本失败: {path}")

        return path

    async def upload_result(self, result_content: str, filename: str) -> str:
        """
        上传测试结果

        Args:
            result_content: 结果内容(JSON)
            filename: 文件名

        Returns:
            结果存储路径
        """
        object_name = f"results/{filename}"
        success, path = self.upload_file(
            file_content=result_content.encode('utf-8'),
            object_name=object_name,
            content_type='application/json'
        )

        if not success:
            raise Exception(f"上传结果失败: {path}")

        return path

    async def upload_report(self, report_content: bytes, filename: str, content_type: str) -> str:
        """
        上传测试报告

        Args:
            report_content: 报告内容
            filename: 文件名
            content_type: 内容类型 (text/html, application/pdf等)

        Returns:
            报告存储路径
        """
        object_name = f"reports/{filename}"
        success, path = self.upload_file(
            file_content=report_content,
            object_name=object_name,
            content_type=content_type
        )

        if not success:
            raise Exception(f"上传报告失败: {path}")

        return path

    async def download_file_async(self, object_path: str) -> bytes:
        """
        异步下载文件（适配async/await）

        Args:
            object_path: 对象路径

        Returns:
            文件内容
        """
        success, content = self.download_file(object_path)

        if not success or content is None:
            raise Exception(f"下载文件失败: {object_path}")

        return content


# 全局单例
_minio_client: Optional[MinIOClient] = None


def get_minio_client() -> MinIOClient:
    """获取MinIO客户端单例"""
    global _minio_client
    if _minio_client is None:
        _minio_client = MinIOClient()
    return _minio_client
