import asyncio
import os
import sys

import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Windows fix for asyncpg
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# PYTHONPATH fix
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)

# Test DB
TEST_DATABASE_URL = "postgresql+asyncpg://test:test@localhost:5433/test_db"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from app.core.db_base import Base
from app.db.session import get_async_session
from app.main import app

# Test engine
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def prepare_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def cleanup_engine():
    yield
    await test_engine.dispose()


@pytest_asyncio.fixture
async def session() -> AsyncSession:
    async with TestSessionLocal() as session:
        yield session


async def override_get_session():
    async with TestSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client():
    app.dependency_overrides[get_async_session] = override_get_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
