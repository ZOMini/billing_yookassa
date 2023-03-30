import asyncio
import datetime
import logging
import time
from http import HTTPStatus

import aiohttp
from aiohttp import ClientSession
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import joinedload, sessionmaker
from sqlalchemy.sql import func, select

from core.config import settings
from db.pg import engine
from models.models_pg import PaymentPG, Tariff, UserStatus

VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT)


async def main_worker():
    DATA_BASE = f'postgresql+asyncpg://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}/{settings.postgres_db}'
    engine = create_async_engine(DATA_BASE)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as pg:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop())) as ahttp:
            current_time = datetime.datetime.now(tz=None)
            scalars = await pg.scalars(select(UserStatus).filter(and_(UserStatus.actual == False, UserStatus.expires_at > current_time)).limit(100))
            for us in scalars:
                ahttp.headers["Authorization"] = f"Bearer {settings.jwt_super}"
                async with ahttp.post(settings.auth_role_url, json = {'role': 'subscriber', 'user': str(us.id)}) as result:
                    if result.status in VALID_HTTP_STATUS:
                        us.actual = True
                        await pg.commit()
                        logging.error('INFO main_worker() - post OK')
                    else:
                        logging.error('ERROR main_worker() - post %s -- %s -- %s', result.status, result.reason, {'role': 'subscriber', 'user': str(us.id)})
            scalars = await pg.scalars(select(UserStatus).filter(and_(UserStatus.actual == True, UserStatus.expires_at < current_time)).limit(100))
            for us in scalars:
                async with ahttp.delete(settings.auth_role_url, headers={'Authorization': f'Bearer {settings.jwt_super}'}, json = {'role': 'subscriber', 'user': str(us.id)}) as result:
                    if result.status in VALID_HTTP_STATUS:
                        us.actual = False
                        await pg.commit()
                        logging.error('INFO main_worker() - delete OK')
                    else:
                        logging.error('ERROR main_worker() - delete %s', result.status)

while True:
    time.sleep(5)
    loop = asyncio.new_event_loop()
    tasks = [main_worker(),]

    async def main():
        await asyncio.gather(*tasks)
    loop.run_until_complete(main())
    logging.error('INFO main_worker() - loop OK')
