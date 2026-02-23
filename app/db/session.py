import os

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://user:password@db:5432/app")

async_engine = create_async_engine(DATABASE_URL, echo=False)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
