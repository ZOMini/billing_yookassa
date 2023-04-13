import asyncio
import datetime
import logging
import time
import uuid
from http import HTTPStatus

import pytest

from models.models_pg import PaymentPG, Tariff, UserStatus
from tests.test_settings import auth_get_role_url
from tests.testdata.api_data import tariff_id
from tests.testdata.worker_data import payment_for_subscription

expires_at_1_day = datetime.datetime.now() + datetime.timedelta(days=1)
expires_at_1_day_ago = datetime.datetime.now() - datetime.timedelta(days=1)
@pytest.mark.parametrize(
    'query_data, expected_answer',
    [({'expires_at': expires_at_1_day, 'sleep': 1, 'actual': False}, {'roles': ({'roles': ['subscriber']},), 'status': 200}),
     ({'expires_at': expires_at_1_day_ago, 'sleep': 2, 'actual': True}, {'roles': ('No roles',), 'status': 404})]
)
@pytest.mark.asyncio
async def test_worker(pg_write_data, get_or_create_user, pg_get_obj_by_id, pg_write_payment_data, make_get_request, clear_pg, query_data, expected_answer):
    """Так как все сильно завязано на сторонние ресурсы,
    то места для маневра очень мало). Чего смогу, то протестирую."""
    user_id = get_or_create_user
    await asyncio.sleep(query_data['sleep'])  #  Разделяем по времени, воркер работает через 1 сек.
    us_id = await pg_write_data(UserStatus, {'id': user_id, 'expires_at': query_data['expires_at'], 'actual': query_data['actual']})
    logging.error('INFO - user_id %s ', us_id)
    # Проверяем совпадают ли user_id и userstatus_id
    assert us_id == user_id
    userstatus: UserStatus = await pg_get_obj_by_id(UserStatus, us_id)
    logging.error('INFO - userstatus.actual %s ', userstatus.actual)
    tariff: Tariff = await pg_get_obj_by_id(Tariff, tariff_id)
    logging.error('INFO - tariff %s ', type(tariff))
    payment: PaymentPG = await pg_write_payment_data(PaymentPG, payment_for_subscription, tariff, userstatus)
    await asyncio.sleep(query_data['sleep'])  # Ждем пока сработает воркер, проверяем что он отработал штатно.
    body, headers, status = await make_get_request(f'{auth_get_role_url}/testuser', {})
    logging.error('INFO - test_role %s ', body)
    # проверяем что роль в auth пользователю выдалась / отозвалась (второй тест).
    assert expected_answer['status'] == status[0]
    assert expected_answer['roles'] == body
