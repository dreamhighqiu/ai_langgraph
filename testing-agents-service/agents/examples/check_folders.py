

import asyncio
from app.db.database import async_session_factory
from sqlalchemy import select
from app.models.folder import Folder

async def check():
    async with async_session_factory() as session:
        result = await session.execute(select(Folder))
        folders = result.scalars().all()
        for f in folders:
            print(f"id={f.id}, name={f.name}, parent_id={f.parent_id}")
# noqa  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZEd4aGVBPT06MzkwZjg2YmQ=

asyncio.run(check())
# type: ignore  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2ZEd4aGVBPT06MzkwZjg2YmQ=

