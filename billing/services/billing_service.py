import datetime
import json
import uuid
from functools import lru_cache
from http import HTTPStatus

from aiohttp import BasicAuth, ClientSession
from aioredis import Redis
from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import select

from core.bill_log import LOGGING_BILL_API
from core.config import settings
from db.abstract import CacheStorage
from db.aiohttp import get_aiohttp
from db.pg import get_pg
from db.rabbitmq import rabbit_conn
from db.redis import get_redis
from models.models_pg import PaymentPG, StatusEnum, Tariff, UserStatus
from services.aio_requests import AioRequests
from services.response_msg import ResponseMsg


class BillingService:
    def __init__(self, cache: Redis, pg: AsyncSession, aiohttp: ClientSession):
        self.cache = cache
        self.pg = pg
        self.aiohttp = aiohttp

    async def post_event(self, user_id: str, event: str):
        try:
            body = {'user_id': user_id, 'event_type': event}
            connection = rabbit_conn()
            channel = connection.channel()
            channel.basic_publish(settings.EXCHANGE, settings.ROUTING_KEY, json.dumps(body))
            connection.close()
            LOGGING_BILL_API.info('RABBIT BILL OK')
        except Exception as e:
            LOGGING_BILL_API.error('RABBIT _post_event() BILL ERROR - %s', e)

    async def _refund_process(self, payment: PaymentPG):
        """Метод непосредственно производит возврат."""
        async with self.aiohttp.post(
            'https://api.yookassa.ru/v3/refunds',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
            headers={'Idempotence-Key': str(uuid.uuid4())},
            json=AioRequests.refund_body(payment)
        ) as result:
            response_obj = await result.json()
            try:
                if response_obj['status'] != StatusEnum.succeeded.value:
                    raise HTTPException(HTTPStatus.BAD_REQUEST, response_obj['status'])
            except KeyError:
                raise HTTPException(HTTPStatus.BAD_REQUEST, response_obj['description'])
        payment.userstatus.expires_at = datetime.datetime.now()
        payment.status = StatusEnum.refund.value

    async def _get_payment_by_userid(self, user_id: uuid.UUID) -> PaymentPG:
        """Метод возвращает последнюю succeeded подписку. Либо 400-тит"""
        scalar = await self.pg.scalars(select(PaymentPG).filter(PaymentPG.userstatus_id == user_id).filter(PaymentPG.status == StatusEnum.refund.value).limit(1))
        refund = scalar.first()
        if refund:
            raise HTTPException(HTTPStatus.BAD_REQUEST, ResponseMsg.BAD_REQUEST_RETRY.value)
        scalar = await self.pg.scalars(select(PaymentPG).options(joinedload(PaymentPG.tariff), joinedload(PaymentPG.userstatus)).filter(PaymentPG.userstatus_id == user_id).filter(PaymentPG.status == 'succeeded').order_by(PaymentPG.created_at.desc()).limit(1))
        payment = scalar.first()
        if not payment:
            raise HTTPException(HTTPStatus.BAD_REQUEST, ResponseMsg.BAD_REQUEST_NO_PAYMENTS.value)
        if payment.created_at + datetime.timedelta(days=3) < datetime.datetime.now():
            raise HTTPException(HTTPStatus.BAD_REQUEST, ResponseMsg.BAD_REQUEST_3_DAYS.value)
        return payment

    async def yoo_refunds(self, user_id: uuid.UUID) -> PaymentPG:
        payment = await self._get_payment_by_userid(user_id)
        await self._refund_process(payment)
        await self.pg.commit()
        return payment

    async def yoo_payment_create(self, user_id: uuid.UUID | str, tarif_id: uuid.UUID | str, redis_id: uuid.UUID | str) -> dict:
        tarif = await self._get_tariff_obj(str(tarif_id))
        async with self.aiohttp.post(
            'https://api.yookassa.ru/v3/payments',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
            json=AioRequests.post_body(user_id, tarif, redis_id),
            headers=AioRequests.post_headers(redis_id)
        ) as payment:
            return await payment.json(), payment.status

    async def yoo_payment_get(self, yoo_id: uuid.UUID | str) -> tuple[dict, str]:
        async with self.aiohttp.get(
            f'https://api.yookassa.ru/v3/payments/{yoo_id}',
            auth=BasicAuth(settings.yoo_account_id, settings.yoo_secret_key),
        ) as payment:
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
        if not yoo_id:
            raise HTTPException(HTTPStatus.NOT_FOUND, f'{redis_id} {ResponseMsg.NOT_FOUND_RETRY.value}')
        return yoo_id

    async def del_redis_pair(self, redis_id: uuid.UUID) -> None:
        """Удаляем пару из редиса."""
        await self.cache.delete(str(redis_id))

    async def _get_tariff_obj(self, id: str | uuid.UUID) -> Tariff:
        tariff = await self.pg.get(Tariff, id)
        if not tariff:
            raise HTTPException(HTTPStatus.NOT_FOUND, ResponseMsg.NOT_FOUND_NO_TARIFF.value)
        return tariff

    async def _get_or_post_userstatus_obj(self, data: dict, tarif: Tariff) -> UserStatus:
        """Метод из PG достает данные по подписке у пользователя.
        Если нет данных - создает. Если статус платежа succeeded продливает/возобновляет/активирует подписку.
        Ставит булевый флаг для воркера, что бы проверить подписку в Auth модуле.
        Возвращает обновленный объект UserStatus."""
        u_obj = await self.pg.get(UserStatus, data['metadata']['user_id'])
        status = True if data['status'] == StatusEnum.succeeded.value else False
        if not u_obj:
            self.pg.add(UserStatus(id=data['metadata']['user_id']))
            u_obj = await self.pg.get(UserStatus, data['metadata']['user_id'])
        u_obj.expires_at = datetime.datetime.now() if not u_obj.expires_at else u_obj.expires_at
        if status and u_obj.expires_at.timestamp() > datetime.datetime.now().timestamp():
            u_obj.expires_at = u_obj.expires_at + tarif.days
        elif status:
            u_obj.expires_at = datetime.datetime.now() + tarif.days
            u_obj.actual = False
        return u_obj

    async def _post_payment_obj(self, data: dict, t_obj: Tariff, u_obj: UserStatus) -> None:
        card_type = data['payment_method']['card']['card_type']
        last4 = data['payment_method']['card']['last4']
        obj = PaymentPG(
            id=data['id'],
            payment=f'{card_type} - **** **** **** {last4}',
            income=float(data['amount']['value']),
            status=data['status'],
            tariff=t_obj,
            userstatus=u_obj)
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
