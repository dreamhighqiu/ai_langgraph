"""
版权所有 (c) 2023-2026 北京慧测信息技术有限公司(但问智能) 保留所有权利。

本代码版权归北京慧测信息技术有限公司(但问智能)所有，仅用于学习交流目的，未经公司商业授权，
不得用于任何商业用途，包括但不限于商业环境部署、售卖或以任何形式进行商业获利。违者必究。

授权商业应用请联系微信：huice666
"""

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
# fmt: off  MC8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hoRFJRPT06MGFkYTI1Yjg=

asyncio.run(check())

# noqa  MS8yOmFIVnBZMlhwZ3JIa3VwSHBuSjQ2Y0hoRFJRPT06MGFkYTI1Yjg=
