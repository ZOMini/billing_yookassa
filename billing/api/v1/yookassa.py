import logging
import uuid
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from services.billing_service import BillingService, get_billing_service
from template.buy_return import html_buy_return
from template.refund import html_refund

router = APIRouter()
VALID_HTTP_STATUS = (HTTPStatus.CREATED, HTTPStatus.OK, HTTPStatus.ACCEPTED)

@router.get('/buy_subscription')
async def get_buy_subscription(
        user_id: uuid.UUID,
        tarif_id: uuid.UUID,
        billing_service: BillingService = Depends(get_billing_service),
    ) -> RedirectResponse:
    """GET метод для браузера. Создает платеж.
    Редиректит на yoomoney - для оплаты.
    Скорее тестовая ручка, пока не понятно."""
    redis_id = str(uuid.uuid4())
    logging.error('INFO redis_id - %s', redis_id)
    payment, status = await billing_service.yoo_payment_create(user_id, tarif_id, redis_id)
    if status not in (VALID_HTTP_STATUS):
        raise HTTPException(status, payment['code'])
    # так как пока не понятно в этом сервисе(callback) или это будет отделный воркер,
    # сохранять id необработанных платежей(+redis id как ключ) буду в редисе.
    redis_result = await billing_service.create_pair_id(redis_id, payment['id'])
    logging.error('INFO redis_result - %s', redis_result)
    return RedirectResponse(payment['confirmation']['confirmation_url'])

@router.post('/buy_subscription')
async def get_buy_subscription(
        user_id: uuid.UUID,
        tarif_id: uuid.UUID,
        billing_service: BillingService = Depends(get_billing_service),
    ) -> str:
    """POST ручка для сервисов. Создает платеж.
    Возвращает ссылку на подтверждение платежа,
    для фронтА например, а фронт уже решает что с этой ссылкой делать."""
    redis_id = str(uuid.uuid4())
    payment, status = await billing_service.yoo_payment_create(user_id, tarif_id, redis_id)
    if status not in (VALID_HTTP_STATUS):
        raise HTTPException(status, payment['code'])
    await billing_service.create_pair_id(redis_id, payment['id'])
    return payment['confirmation']['confirmation_url']

@router.get('/buy_return/{redis_id}')
async def get_buy_return(
    redis_id: uuid.UUID,
    billing_service: BillingService = Depends(get_billing_service),
    ) -> HTMLResponse:
    """Ручка return_url с Юкассы. Добавляет в PG платеж,
    если статут succeded - то дальше работает воркер."""
    yoo_id = await billing_service.get_yoo_id(redis_id)
    payment, status = await billing_service.yoo_payment_get(yoo_id)
    if status not in VALID_HTTP_STATUS:
        raise HTTPException(status, payment['code'])
    await billing_service.post_payment_pg(payment)
    await billing_service.post_event(payment['metadata']['user_id'], 'payment_accepted')
    await billing_service.del_redis_pair(redis_id)
    template = html_buy_return(payment['metadata']['user_id'], payment['status'], payment['description'])
    return HTMLResponse(template, HTTPStatus.OK)

@router.get('/refunds_subscription/{user_id}')
async def get_buy_subscription(
        user_id: uuid.UUID,
        billing_service: BillingService = Depends(get_billing_service),
    ) -> RedirectResponse:
    """GET HTML метод для браузера. По id пользователя и сумме делает возврат,
    в рамках последней успешной транзакции."""
    payment = await billing_service.yoo_refunds(user_id)
    await billing_service.post_event(str(payment.userstatus_id), 'payment_refund')
    template = html_refund(user_id)
    return HTMLResponse(template, HTTPStatus.OK)
