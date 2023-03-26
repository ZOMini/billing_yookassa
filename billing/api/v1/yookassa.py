import logging
import uuid

from fastapi import APIRouter, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from template.buy_return import html_buy_return
from yookassa import Configuration, Payment
from yookassa.domain.models.confirmation.response.confirmation_redirect import (
    ConfirmationRedirect
)
from yookassa.domain.response import PaymentListResponse, PaymentResponse

from services.billing_service import BillingService, get_billing_service

Configuration.account_id = '206307'
Configuration.secret_key = 'test_Z4fOU6TyaN-zLM742YzD2l8UeNGxdoFBTMj14bGWkHY'

router = APIRouter()


@router.get('/buy_subscription/{user_id}')
async def get_buy_subscription(
        user_id: uuid.UUID,
        billing_service: BillingService = Depends(get_billing_service),
    ) -> RedirectResponse:
    """GET HTTP метод. Создает платеж. Редиректит на yoomoney - для оплаты."""
    redis_id = str(uuid.uuid4())
    logging.error('INFO redis_id - %s', redis_id)
    # payment = Payment.create(redis_id)  # Через SDK - sync
    payment = await billing_service.yoo_payment_create(user_id, redis_id)
    redis_result = await billing_service.create_pair_id(redis_id, payment['id'])
    logging.error('INFO redis_result - %s', redis_result)
    return RedirectResponse(payment['confirmation']['confirmation_url'])


@router.get('/buy_return/{redis_id}')
async def get_buy_return(
    redis_id: uuid.UUID,
    billing_service: BillingService = Depends(get_billing_service),
    ) -> HTMLResponse:
    """buy_return."""
    yoo_id = await billing_service.get_yoo_id(redis_id)
    logging.error('INFO redis_value - %s', yoo_id)
    # payment = Payment.find_one(yoo_id)  # Через SDK - sync
    payment = await billing_service.yoo_payment_get(yoo_id)
    await billing_service.post_payment_pg(payment)
    template = html_buy_return(payment['metadata']['user_id'], payment['status'], payment['created_at'])
    return HTMLResponse(template, 200)
