"""
测试文件夹API，检查是否正确返回根文件夹
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

