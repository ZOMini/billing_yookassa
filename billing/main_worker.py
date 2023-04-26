import asyncio
import time
from http import HTTPStatus

import aiohttp
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.bill_log import logging
from core.config import settings
from worker_core.worker_service import (
    del_subscriber,
    expires_subscriber,
    post_subscriber
)

VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT)
logger = logging.getLogger(__name__)


async def main_worker():
    data_base = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
    engine = create_async_engine(data_base)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    loop = asyncio.get_event_loop()
    async with async_session() as pg:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=loop)) as ahttp:
            await post_subscriber(pg, ahttp)
            await del_subscriber(pg, ahttp)
            await expires_subscriber(pg)
            await asyncio.sleep(0)
    await engine.dispose()
    await ahttp.close()


while True:
    time.sleep(1)
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main_worker())
    loop.close()
    logger.info('main_worker() - loop OK')
