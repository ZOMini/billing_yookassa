import datetime
import logging
from http import HTTPStatus

from aiohttp import ClientSession
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from core.config import settings
from models.models_pg import PaymentPG, Tariff, UserStatus

VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT)


async def post_subscriber(pg: AsyncSession, ahttp: ClientSession):
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

async def del_subscriber(pg: AsyncSession, ahttp: ClientSession):
    current_time = datetime.datetime.now(tz=None)
    scalars = await pg.scalars(select(UserStatus).filter(and_(UserStatus.actual == True, UserStatus.expires_at < current_time)).limit(100))
    for us in scalars:
        async with ahttp.delete(settings.auth_role_url, headers={'Authorization': f'Bearer {settings.jwt_super}'}, json = {'role': 'subscriber', 'user': str(us.id)}) as result:
            if result.status in VALID_HTTP_STATUS:
                us.actual = False
                await pg.commit()
                logging.error('INFO main_worker() - delete OK')
            else:
                logging.error('ERROR main_worker() - delete %s', result.status)
