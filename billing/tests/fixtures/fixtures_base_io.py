import asyncio
import logging

import aiohttp
import aioredis
import pytest
import pytest_asyncio
from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from core.config import settings
from tests.test_settings import pg_bill_url, redis_url

DATA_BASE = pg_bill_url
engine = create_async_engine(DATA_BASE, echo=True, query_cache_size=0)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def pg_client():
    async_session: AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False, autoflush=True)
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="session")
async def redis_client():
    redis: Redis = await aioredis.from_url(redis_url, decode_responses=True, max_connections=20)
    yield redis
    # await redis.flushall()
    await redis.close()


@pytest_asyncio.fixture(scope="session")
async def ahttp_client() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop(), verify_ssl=False))
    yield session
    await session.close()
