import asyncio

import aiohttp
import aioredis
import pytest
import pytest_asyncio
from aioredis import Redis
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from core.config import settings


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


# @pytest_asyncio.fixture(scope="session")
# async def pg_client():
#     DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
#     engine = create_async_engine(DATA_BASE, echo=True)
#     async_session: AsyncSession = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#     yield async_session
#     await async_session.close()


# @pytest.fixture(scope='session')
# async def redis_client():
#     redis: Redis = await aioredis.from_url(
#         f'redis://{settings.redis_bill}:{settings.redis_port}',
#         decode_responses=True, max_connections=20)
#     yield redis
#     await redis.flushall()
#     await redis.close()
    

@pytest_asyncio.fixture(scope="session")
async def ahttp_client() -> aiohttp.ClientSession:
    session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop(), verify_ssl=False))
    yield session
    await session.close()
