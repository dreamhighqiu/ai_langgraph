"""数据库服务 - 统一的数据库操作接口.

支持：
- Tortoise ORM (MySQL/PostgreSQL/SQLite)
- 连接池管理
- 事务支持
- 模型动态加载

可以被多个应用共享：
- testing-deep-agents-service
- autogen_study
"""

import os
import logging
from typing import Optional, Dict, Any, List, Type
from dataclasses import dataclass
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "")
MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
MYSQL_DB = os.getenv("MYSQL_DB", "ai_db")


@dataclass
class DatabaseConfig:
    """数据库配置."""
    engine: str = "tortoise.backends.mysql"
    host: str = MYSQL_HOST
    port: int = MYSQL_PORT
    user: str = MYSQL_USER
    password: str = MYSQL_PASSWORD
    database: str = MYSQL_DB
    charset: str = "utf8mb4"
    minsize: int = 1
    maxsize: int = 10
    connect_timeout: int = 60
    pool_recycle: int = 300
    
    def to_tortoise_config(self, models: List[str] = None) -> Dict[str, Any]:
        """转换为 Tortoise ORM 配置格式."""
        models = models or ["aerich.models"]
        
        return {
            "connections": {
                "default": {
                    "engine": self.engine,
                    "credentials": {
                        "host": self.host,
                        "port": self.port,
                        "user": self.user,
                        "password": self.password,
                        "database": self.database,
                        "charset": self.charset,
                        "minsize": self.minsize,
                        "maxsize": self.maxsize,
                        "connect_timeout": self.connect_timeout,
                        "pool_recycle": self.pool_recycle,
                        "echo": False,
                    }
                }
            },
            "apps": {
                "models": {
                    "models": models,
                    "default_connection": "default",
                }
            },
            "use_tz": False,
            "timezone": "Asia/Shanghai",
        }


class DatabaseService:
    """数据库服务.
    
    提供统一的数据库操作接口，支持：
    - 连接管理
    - CRUD 操作
    - 事务处理
    - 健康检查
    """
    
    _instance: Optional["DatabaseService"] = None
    _initialized: bool = False
    
    @classmethod
    def get_instance(cls) -> "DatabaseService":
        """获取单例实例."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def __init__(self, config: Optional[DatabaseConfig] = None):
        """初始化数据库服务.
        
        Args:
            config: 数据库配置，如果不指定则使用环境变量
        """
        self.config = config or DatabaseConfig()
        self._tortoise_config: Optional[Dict[str, Any]] = None
    
    async def init(self, models: List[str] = None) -> bool:
        """初始化数据库连接.
        
        Args:
            models: 模型模块列表
            
        Returns:
            是否初始化成功
        """
        if self._initialized:
            logger.info("Database already initialized")
            return True
        
        try:
            from tortoise import Tortoise
            
            self._tortoise_config = self.config.to_tortoise_config(models)
            
            # 关闭可能存在的旧连接
            try:
                await Tortoise.close_connections()
            except Exception:
                pass
            
            # 初始化新连接
            await Tortoise.init(config=self._tortoise_config)
            
            # 测试连接
            conn = Tortoise.get_connection("default")
            await conn.execute_query("SELECT 1")
            
            self._initialized = True
            logger.info(f"Database connected: {self.config.host}:{self.config.port}/{self.config.database}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            return False
    
    async def close(self):
        """关闭数据库连接."""
        if not self._initialized:
            return
        
        try:
            from tortoise import Tortoise
            await Tortoise.close_connections()
            self._initialized = False
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database: {e}")
    
    async def generate_schemas(self, safe: bool = True):
        """生成数据库表结构.
        
        Args:
            safe: 如果为 True，只创建不存在的表
        """
        try:
            from tortoise import Tortoise
            await Tortoise.generate_schemas(safe=safe)
            logger.info("Database schemas generated")
        except Exception as e:
            logger.error(f"Failed to generate schemas: {e}")
            raise
    
    @asynccontextmanager
    async def transaction(self):
        """事务上下文管理器."""
        from tortoise.transactions import in_transaction
        
        async with in_transaction() as connection:
            yield connection
    
    async def execute_query(
        self,
        query: str,
        params: Optional[List[Any]] = None,
    ) -> List[Dict[str, Any]]:
        """执行原生 SQL 查询.
        
        Args:
            query: SQL 查询语句
            params: 查询参数
            
        Returns:
            查询结果列表
        """
        try:
            from tortoise import Tortoise
            
            conn = Tortoise.get_connection("default")
            result = await conn.execute_query(query, params)
            
            # result 是元组 (affected_rows, results)
            if isinstance(result, tuple) and len(result) > 1:
                return result[1]  # 返回结果集
            return []
            
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise RuntimeError(f"查询执行失败: {e}")
    
    async def execute_many(
        self,
        query: str,
        params_list: List[List[Any]],
    ) -> int:
        """批量执行 SQL.
        
        Args:
            query: SQL 语句
            params_list: 参数列表
            
        Returns:
            影响的行数
        """
        try:
            from tortoise import Tortoise
            
            conn = Tortoise.get_connection("default")
            total_affected = 0
            
            for params in params_list:
                result = await conn.execute_query(query, params)
                if isinstance(result, tuple):
                    total_affected += result[0]
            
            return total_affected
            
        except Exception as e:
            logger.error(f"Batch execution failed: {e}")
            raise RuntimeError(f"批量执行失败: {e}")
    
    # =========================================================================
    # 通用 CRUD 操作
    # =========================================================================
    
    async def create(
        self,
        model_class: Type,
        data: Dict[str, Any],
    ) -> Any:
        """创建记录.
        
        Args:
            model_class: Tortoise 模型类
            data: 数据字典
            
        Returns:
            创建的模型实例
        """
        try:
            instance = model_class(**data)
            await instance.save()
            return instance
        except Exception as e:
            logger.error(f"Create failed: {e}")
            raise RuntimeError(f"创建记录失败: {e}")
    
    async def get_by_id(
        self,
        model_class: Type,
        id: Any,
    ) -> Optional[Any]:
        """根据 ID 获取记录.
        
        Args:
            model_class: Tortoise 模型类
            id: 记录 ID
            
        Returns:
            模型实例或 None
        """
        try:
            return await model_class.get_or_none(id=id)
        except Exception as e:
            logger.error(f"Get by ID failed: {e}")
            return None
    
    async def get_list(
        self,
        model_class: Type,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 100,
    ) -> List[Any]:
        """获取记录列表.
        
        Args:
            model_class: Tortoise 模型类
            filters: 过滤条件
            order_by: 排序字段列表
            offset: 偏移量
            limit: 限制数量
            
        Returns:
            模型实例列表
        """
        try:
            query = model_class.all()
            
            if filters:
                query = query.filter(**filters)
            
            if order_by:
                query = query.order_by(*order_by)
            
            return await query.offset(offset).limit(limit)
            
        except Exception as e:
            logger.error(f"Get list failed: {e}")
            return []
    
    async def update(
        self,
        model_class: Type,
        id: Any,
        data: Dict[str, Any],
    ) -> Optional[Any]:
        """更新记录.
        
        Args:
            model_class: Tortoise 模型类
            id: 记录 ID
            data: 更新数据
            
        Returns:
            更新后的模型实例或 None
        """
        try:
            instance = await model_class.get_or_none(id=id)
            if not instance:
                return None
            
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            
            await instance.save()
            return instance
            
        except Exception as e:
            logger.error(f"Update failed: {e}")
            raise RuntimeError(f"更新记录失败: {e}")
    
    async def delete(
        self,
        model_class: Type,
        id: Any,
    ) -> bool:
        """删除记录.
        
        Args:
            model_class: Tortoise 模型类
            id: 记录 ID
            
        Returns:
            是否删除成功
        """
        try:
            instance = await model_class.get_or_none(id=id)
            if not instance:
                return False
            
            await instance.delete()
            return True
            
        except Exception as e:
            logger.error(f"Delete failed: {e}")
            return False
    
    async def count(
        self,
        model_class: Type,
        filters: Optional[Dict[str, Any]] = None,
    ) -> int:
        """统计记录数.
        
        Args:
            model_class: Tortoise 模型类
            filters: 过滤条件
            
        Returns:
            记录数量
        """
        try:
            query = model_class.all()
            
            if filters:
                query = query.filter(**filters)
            
            return await query.count()
            
        except Exception as e:
            logger.error(f"Count failed: {e}")
            return 0
    
    # =========================================================================
    # 健康检查
    # =========================================================================
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查."""
        try:
            from tortoise import Tortoise
            
            if not self._initialized:
                return {
                    "status": "not_initialized",
                    "host": self.config.host,
                    "database": self.config.database,
                }
            
            conn = Tortoise.get_connection("default")
            await conn.execute_query("SELECT 1")
            
            return {
                "status": "healthy",
                "host": self.config.host,
                "port": self.config.port,
                "database": self.config.database,
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "host": self.config.host,
                "database": self.config.database,
                "error": str(e),
            }
