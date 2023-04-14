import logging
from http import HTTPStatus

import pytest

from tests.test_settings import create_url
from tests.testdata.api_data import tariff_id, user_create_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [({'query': user_create_data, 'tariff': tariff_id},
      {'status_create': HTTPStatus.OK, 'redis_cnt': 1}, ),]
)
@pytest.mark.asyncio
async def test_create_payment(make_post_request, get_redis_keys, get_or_create_user, query_data, expected_answer):
    """Так как все сильно завязано на сторонний ресурс,
    то места для маневра очень мало). Чего смогу, то протестирую."""
    user_id = get_or_create_user
    _tariff = query_data['tariff']
    body, headers, status = await make_post_request(create_url, {'user_id': user_id, 'tarif_id': _tariff}, {})
    assert status[0] == expected_answer['status_create']
    #  Тестируем что в ответ получили ссылку на платеж.
    assert 'https://yoomoney.ru/checkout/payments/v2/contract' in body[0]
    redis_keys = await get_redis_keys()
    #  Тестируем что создалась пара ключей в редисе.
    assert len(redis_keys[1]) == expected_answer['redis_cnt']
