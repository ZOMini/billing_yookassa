import datetime
import json
import logging
import math
import uuid
from functools import lru_cache

from aiohttp import BasicAuth, ClientResponse, ClientSession
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import func, select
from yookassa import Payment
from yookassa.domain.response import PaymentResponse

from core.config import settings
from db.abstract import CacheStorage
from db.aiohttp import get_aiohttp
from db.pg import get_pg
from db.redis import get_redis
from models.models_pg import PaymentPG, Tariff, UserStatus
from services.aio_requests import AioRequests


class BillingService:
    def __init__(self, cache: CacheStorage, pg: AsyncSession, aiohttp: ClientSession):
        self.cache = cache
        self.pg = pg
        self.aiohttp = aiohttp

    async def _refund_process(self, summ: int, payment: PaymentPG, refund_days: int):
        """Метод непосредственно производит возврат."""
        async with self.aiohttp.post(
            'https://api.yookassa.ru/v3/refunds',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
            headers={'Idempotence-Key': str(uuid.uuid4())},
            json=AioRequests.refund_body(payment, summ)
        ) as result:
            response_obj = await result.json()
            logging.error('zzzzzzzzzzzzzzzzzzzzz max_refund %s', response_obj)
            try:
                if response_obj['status'] != 'succeeded':
                    raise HTTPException(400, response_obj['status'])
            except KeyError:
                raise HTTPException(400, response_obj['description'])
        payment.userstatus.expires_at = payment.userstatus.expires_at - datetime.timedelta(days=refund_days)
        # if payment.userstatus.expires_at.timestamp() < datetime.datetime.now().timestamp():
        #     payment.userstatus.actual = False

    async def _calculation_refund(self, summ: int, payment: PaymentPG):
        """Метод счетает количество дней заявленных для возврата."""
        days_remained = (payment.userstatus.expires_at - datetime.datetime.now()).days
        if days_remained <= 0:
            raise HTTPException(400, 'Возврат не возможен. Подписка не активна.')
        price_day = payment.income / payment.tariff.days.days
        max_refund = days_remained * price_day
        refund_days = math.ceil(summ / price_day)
        logging.error('zzzzzzzzzzzzzzzzzzzzz max_refund %s --- %s', max_refund, summ)
        if max_refund < summ:
            raise HTTPException(400, 'Возврат не возможен. Сумма запрошенная на возврат, больше максимально возможной.')
        return refund_days

    async def _get_payment_by_userid(self, user_id: uuid.UUID) -> PaymentPG:
        """Метод возвращает последнюю succeeded подписку. Либо 400-тит"""
        scalar = await self.pg.scalars(select(PaymentPG).options(joinedload(PaymentPG.tariff), joinedload(PaymentPG.userstatus)).filter(PaymentPG.userstatus_id == user_id).filter(PaymentPG.status == 'succeeded').order_by(PaymentPG.created_at.desc()).limit(1))
        payment = scalar.first()
        if not payment:
            raise HTTPException(400, 'Возврат не возможен. У пользователя нет оплаченных подписок.')
        return payment
        
    async def yoo_refunds(self, user_id: uuid.UUID, summ: int):
        payment = await self._get_payment_by_userid(user_id)
        refund_days = await self._calculation_refund(summ, payment)
        await self._refund_process(summ, payment, refund_days)
        await self.pg.commit()
        logging.error('aaaaaaaaaaaaaaa True')

    async def yoo_payment_create(self, user_id: uuid.UUID | str, tarif_id: uuid.UUID | str, redis_id: uuid.UUID | str) -> dict:
        tarif = await self._get_tariff_obj(tarif_id)
        async with self.aiohttp.post(
            'https://api.yookassa.ru/v3/payments',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
            json=AioRequests.post_body(tarif.price, user_id, tarif_id, redis_id),
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
        """Создаем пару id. Ключ redis_id, значение yoo_payment_id(id платежа в yookasse).
        Это необходимо т.к. до создания платежа в yookasse мы не знаем payment_id, передать свой не возможно,
        а при создании платежа уже нужно передать return_url(в котором квари параметр какой либо id,
        для идентификации - кого/какой платеж, вернуло после платежа). 
        Ну либо callback - но уже через редис решил, так гибче получается."""
        result = await self.cache.set(redis_id, yoo_id, settings.redis_expire)
        return result

    async def get_yoo_id(self, redis_id: uuid.UUID) -> str | None:
        """А тут мы получаем по radis_id(из квари параметра return_url) - payment_id yookass'ы."""
        yoo_id = await self.cache.get(str(redis_id))
        logging.error('INFO redis_yoo_id - %s', yoo_id)
        return yoo_id

    async def _get_tariff_obj(self, id: str | uuid.UUID) -> Tariff:
        tariff = await self.pg.get(Tariff, id)
        if not tariff:
            raise HTTPException(404, 'Нет такого тарифа.')
        return tariff

    async def _get_or_post_userstatus_obj(self, data: dict, tarif: Tariff) -> UserStatus:
        """Метод из PG достает данные по подписке у пользователя.
        Если нет данных - создает. Если статус платежа succeeded продливает/возобновляет/активирует подписку.
        Ставит булевый флаг для воркера, что бы проверить подписку в Auth модуле.
        Возвращает обновленный объект UserStatus."""
        u_obj = await self.pg.get(UserStatus, data['metadata']['user_id'])
        status = True if data['status'] == 'succeeded' else False
        if not u_obj:
            self.pg.add(UserStatus(id=data['metadata']['user_id']))
            u_obj = await self.pg.get(UserStatus, data['metadata']['user_id'])
        u_obj.expires_at = datetime.datetime.now() if not u_obj.expires_at else u_obj.expires_at
        if status and u_obj.expires_at.timestamp() > datetime.datetime.now().timestamp():
            u_obj.expires_at = u_obj.expires_at + tarif.days
        elif status:
            u_obj.expires_at = datetime.datetime.now() + tarif.days
            u_obj.actual = False
        # await self.pg.commit()
        return u_obj

    async def _post_payment_obj(self, data: dict, t_obj: Tariff, u_obj: UserStatus) -> None:
        card_type = data['payment_method']['card']['card_type']
        last4 = data['payment_method']['card']['last4']
        logging.error('11111111111111111111111111 - %s', u_obj)
        obj =  PaymentPG(
            id=data['id'],
            payment=f'{card_type} - **** **** **** {last4}',
            income=float(data['income_amount']['value']),
            status=data['status'],
            tariff=t_obj,
            userstatus=u_obj)
        logging.error('post_payment_pg - %s', obj.__dict__)
        self.pg.add(obj)

    async def post_payment_pg(self, data: dict) -> None:
        tariff = await self._get_tariff_obj(data['metadata']['tarif_id'])
        userstatus = await self._get_or_post_userstatus_obj(data, tariff)
        await self._post_payment_obj(data, tariff, userstatus)
        await self.pg.commit()


@lru_cache()
def get_billing_service(
    cache: CacheStorage = Depends(get_redis),
    pg: AsyncSession = Depends(get_pg),
    aiohttp: ClientSession = Depends(get_aiohttp)
) -> BillingService:
    return BillingService(cache, pg, aiohttp)
