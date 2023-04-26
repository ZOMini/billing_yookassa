import datetime
import json
import logging
from http import HTTPStatus

from aiohttp import ClientSession
from sqlalchemy import and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func, select

from core.bill_log import LOGGING_BILL_WORKER
from core.config import settings
from db.rabbitmq import rabbit_conn
from models.models_pg import UserStatus

VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED, HTTPStatus.NO_CONTENT)


async def _worker_post_event(user_id: str, event: str) -> None:
    try:
        body = {'user_id': user_id, 'event_type': event}
        connection = rabbit_conn()
        channel = connection.channel()
        channel.basic_publish(settings.EXCHANGE, settings.ROUTING_KEY, json.dumps(body))
        LOGGING_BILL_WORKER.info('INFO RABBIT worker_post_event() BILL - OK')
        connection.close()
    except Exception as e:
        LOGGING_BILL_WORKER.error('ERROR RABBIT worker_post_event() BILL ERROR - %s', e)


async def post_subscriber(pg: AsyncSession, ahttp: ClientSession) -> None:
    current_time = datetime.datetime.now(tz=None)
    scalars = await pg.scalars(select(UserStatus).filter(and_(
        UserStatus.actual == False,
        UserStatus.expires_at > current_time)).limit(100))
    for us in scalars:
        ahttp.headers["Authorization"] = f"Bearer {settings.jwt_super}"
        async with ahttp.post(settings.auth_role_url,
                              json={'role': 'subscriber', 'user': str(us.id)}) as result:
            if result.status in VALID_HTTP_STATUS:
                us.actual = True
                await pg.commit()
                LOGGING_BILL_WORKER.info('INFO post_subscriber() - post OK')
            else:
                LOGGING_BILL_WORKER.error('ERROR post_subscriber() - post %s -- %s -- %s', result.status, result.reason, {'role': 'subscriber', 'user': str(us.id)})


async def del_subscriber(pg: AsyncSession, ahttp: ClientSession) -> None:
    current_time = datetime.datetime.now(tz=None)
    scalars = await pg.scalars(select(UserStatus).filter(and_(
        UserStatus.actual == True,
        UserStatus.expires_at < current_time)).limit(100))
    for us in scalars:
        async with ahttp.delete(settings.auth_role_url,
                                headers={'Authorization': f'Bearer {settings.jwt_super}'},
                                json={'role': 'subscriber', 'user': str(us.id)}) as result:
            if result.status in VALID_HTTP_STATUS:
                us.actual = False
                us.expires_status = True
                await pg.commit()
                await _worker_post_event(str(us.id), 'subscription_expired')
                LOGGING_BILL_WORKER.info('INFO main_worker() - delete OK')
            else:
                LOGGING_BILL_WORKER.error('ERROR main_worker() - delete %s', result.status)


async def expires_subscriber(pg: AsyncSession) -> None:
    current_time = datetime.datetime.now(tz=None)
    scalars = await pg.scalars(select(UserStatus).filter(and_(
        UserStatus.expires_status == False,
        UserStatus.expires_at < current_time + datetime.timedelta(days=1))).limit(100))
    for us in scalars:
        us.expires_status = True
        await pg.commit()
        await _worker_post_event(str(us.id), 'subscription_expires')
        LOGGING_BILL_WORKER.info('INFO expires_subscriber() - OK')
