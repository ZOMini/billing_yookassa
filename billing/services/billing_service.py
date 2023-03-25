import logging
import uuid
from functools import lru_cache

from fastapi import Depends
from sqlalchemy.orm import Session, scoped_session
from yookassa import Configuration, Payment
from yookassa.domain.models.confirmation.response.confirmation_redirect import (
    ConfirmationRedirect
)
from yookassa.domain.models.payment_data.response.credit_card import CreditCard
from yookassa.domain.models.payment_data.response.payment_data_bank_card import (
    PaymentDataBankCard
)
from yookassa.domain.response import PaymentListResponse, PaymentResponse

from db.abstract import CacheStorage, DataStorage
from db.pg import get_pg
from db.redis import get_redis
from models.models_pg import PaymentPG


class BillingService:
    def __init__(self, cache: CacheStorage, pg: scoped_session[Session]):
        self.cache = cache
        self.pg = pg

    def payment_create(self, user_id: uuid.UUID | str, redis_id: uuid.UUID | str) -> PaymentResponse:
        payment: PaymentResponse = Payment.create({
            "amount": {
                "value": "100.00",
                "currency": "RUB"
            },
            "metadata": {
                'user_id': str(user_id)
            },
            "payment_method_data": {
                "type": "bank_card"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": f"https://localhost/yookassa/api/v1/buy_return/{redis_id}"
            },
            "capture": True,
            "description": "Покупка подписки на месяц"
        }, redis_id)
        logging.error('INFO payment.confirmation.confirmation_url - %s -- type - %s', str(payment.confirmation.confirmation_url), type(payment.confirmation))
        logging.error('INFO payment.json() - %s', payment.json())
        logging.error('INFO payment.id - %s', payment.id)
        logging.error('INFO payment.metadata.user_id - %s', payment.metadata['user_id'])
        return payment


    async def create_pair_id(self, redis_id: uuid.UUID, yoo_id: uuid.UUID):
        result = await self.cache.set(redis_id, yoo_id)
        return result

    async def get_yoo_id(self, redis_id: uuid.UUID):
        result = await self.cache.get(str(redis_id))
        logging.error('INFO redis_result - %s', result)
        return result

    def post_payment_pg(self, data: PaymentResponse):
        obj =  PaymentPG(
            id=data.id,
            user_id=data.metadata['user_id'],
            created_at=data.captured_at,
            amount=float(data.amount.value),
            payment=f'{data.payment_method.card.card_type} - **** **** **** {data.payment_method.card.last4}',
            status=data.status,
            role_granted=False)
        logging.error('post_payment_pg - %s', obj.__dict__)
        self.pg.add(obj)
        self.pg.commit()
        


@lru_cache()
def get_billing_service(
        cache: CacheStorage = Depends(get_redis),
        pg: DataStorage = Depends(get_pg),
) -> BillingService:
    return BillingService(cache, pg)
