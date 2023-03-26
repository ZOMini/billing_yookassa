import json
import logging
import uuid
from functools import lru_cache

from aiohttp import BasicAuth, ClientResponse, ClientSession
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from yookassa import Payment
from yookassa.domain.response import PaymentResponse

from core.config import settings
from db.abstract import CacheStorage
from db.aiohttp import get_aiohttp
from db.pg import get_pg
from db.redis import get_redis
from models.models_pg import PaymentPG
from services.aio_requests import AioRequests


class BillingService:
    def __init__(self, cache: CacheStorage, pg: AsyncSession, aiohttp: ClientSession):
        self.cache = cache
        self.pg = pg
        self.aiohttp = aiohttp

    async def yoo_payment_create(self, user_id: uuid.UUID | str, redis_id: uuid.UUID | str) -> dict:
        async with self.aiohttp.post(
            'https://api.yookassa.ru/v3/payments',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
            json=AioRequests.post_body(user_id, redis_id),
            headers=AioRequests.post_headers(redis_id)
        ) as payment:
            logging.error('INFO payment.json() %s', await payment.json())
            return await payment.json(), payment.status

    async def yoo_payment_get(self, yoo_id: uuid.UUID | str) -> dict:
        async with self.aiohttp.get(
            f'https://api.yookassa.ru/v3/payments/{yoo_id}',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
        ) as payment:
            logging.error('INFO payment.json() %s', await payment.json())
            return await payment.json(), payment.status

    async def create_pair_id(self, redis_id: uuid.UUID, yoo_id: uuid.UUID) -> bool:
        result = await self.cache.set(redis_id, yoo_id, settings.redis_expire)
        return result

    async def get_yoo_id(self, redis_id: uuid.UUID) -> str | None:
        yoo_id = await self.cache.get(str(redis_id))
        logging.error('INFO redis_yoo_id - %s', yoo_id)
        return yoo_id

    async def post_payment_pg(self, data: dict) -> None:
        card_type = data['payment_method']['card']['card_type']
        last4 = data['payment_method']['card']['last4']
        obj =  PaymentPG(
            id=data['id'],
            user_id=data['metadata']['user_id'],
            amount=float(data['amount']['value']),
            payment=f'{card_type} - **** **** **** {last4}',
            status=data['status'])
        logging.error('post_payment_pg - %s', obj.__dict__)
        self.pg.add(obj)
        await self.pg.commit()


@lru_cache()
def get_billing_service(
    cache: CacheStorage = Depends(get_redis),
    pg: AsyncSession = Depends(get_pg),
    aiohttp: ClientSession = Depends(get_aiohttp)
) -> BillingService:
    return BillingService(cache, pg, aiohttp)
