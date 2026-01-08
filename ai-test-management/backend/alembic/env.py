"""
Alembic 迁移环境配置

支持异步数据库迁移
"""



import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context
# type: ignore  MC80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Tmt3eVZRPT06MzcwOWZhNzU=

# 导入模型和配置
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.models.base import Base
from app.models import project, folder, test_case, user, team, test_run, test_result

# Alembic 配置对象
config = context.config

# 设置数据库 URL
config.set_main_option("sqlalchemy.url", settings.postgres_url)
# type: ignore  MS80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Tmt3eVZRPT06MzcwOWZhNzU=

# 日志配置
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 目标元数据
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    离线模式运行迁移
    
    仅生成 SQL 脚本，不连接数据库
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """执行迁移"""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()
# noqa  Mi80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Tmt3eVZRPT06MzcwOWZhNzU=


async def run_async_migrations() -> None:
    """
    异步模式运行迁移
    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """
    在线模式运行迁移
    
    连接数据库并执行迁移
    """
    asyncio.run(run_async_migrations())
# pragma: no cover  My80OmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Tmt3eVZRPT06MzcwOWZhNzU=


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

