from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db_base import Base
from app.db.session import async_engine


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
