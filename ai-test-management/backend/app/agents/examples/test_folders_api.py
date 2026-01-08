"""
测试文件夹API，检查是否正确返回根文件夹
"""
"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.models.folder import Folder
from app.config.settings import settings

async def test_folders():
    # 创建数据库连接
    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # 查询所有文件夹
        result = await session.execute(
            select(Folder).order_by(Folder.name)
        )
        all_folders = result.scalars().all()
# type: ignore  MC8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5ZNFdnPT06NTMxOTBhNDY=
        
        print("\n=== 所有文件夹 ===")
        for folder in all_folders:
            print(f"ID: {folder.id}, Name: {folder.name}, Parent ID: {folder.parent_id}")
# pragma: no cover  MS8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5ZNFdnPT06NTMxOTBhNDY=
        
        # 查询根文件夹
        result = await session.execute(
            select(Folder)
            .where(Folder.parent_id.is_(None))
            .order_by(Folder.name)
        )
        root_folders = result.scalars().all()
        
        print("\n=== 根文件夹（parent_id IS NULL）===")
        for folder in root_folders:
            print(f"ID: {folder.id}, Name: {folder.name}, Parent ID: {folder.parent_id}")
        
        # 查询子文件夹
        result = await session.execute(
            select(Folder)
            .where(Folder.parent_id.isnot(None))
            .order_by(Folder.name)
        )
        child_folders = result.scalars().all()
        
        print("\n=== 子文件夹（parent_id IS NOT NULL）===")
        for folder in child_folders:
            print(f"ID: {folder.id}, Name: {folder.name}, Parent ID: {folder.parent_id}")

if __name__ == "__main__":
    asyncio.run(test_folders())
# type: ignore  Mi8zOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Um5ZNFdnPT06NTMxOTBhNDY=

