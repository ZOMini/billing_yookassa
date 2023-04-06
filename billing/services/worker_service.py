import asyncio

import aiohttp
from aiohttp import ClientSession
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from core.config import settings

# async def pg_conn() -> AsyncSession:
#     DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
#     engine = create_async_engine(DATA_BASE)
#     async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
#     async with async_session() as session:
#         return session

async def ahttp_conn() -> ClientSession:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop())) as ahttp:
        return ahttp

DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
engine = create_async_engine(DATA_BASE)
async_session = async_sessionmaker(engine, expire_on_commit=False)
