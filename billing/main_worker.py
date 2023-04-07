import asyncio
import logging
import time
from http import HTTPStatus

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from worker_core.worker_service import (
    del_subscriber,
    expires_subscriber,
    post_subscriber
)

from core.config import settings
from models.models_pg import PaymentPG, Tariff, UserStatus

VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT)


async def main_worker():
    DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
    engine = create_async_engine(DATA_BASE)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    loop = asyncio.get_event_loop()
    async with async_session() as pg:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=loop)) as ahttp:
            await post_subscriber(pg, ahttp)
            await del_subscriber(pg, ahttp)
            # await expires_subscriber(pg)
    await engine.dispose()

while True:
    time.sleep(5)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_worker())
    loop.close()
    logging.error('INFO main_worker() - loop OK')
