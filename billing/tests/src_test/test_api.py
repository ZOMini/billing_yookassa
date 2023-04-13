import logging
from http import HTTPStatus

import pytest

from tests.test_settings import auth_url, create_url
from tests.testdata.api_data import tariff, user_create_data


@pytest.mark.parametrize(
    'query_data, expected_answer',
    [({'query': user_create_data, 'tariff': tariff},
      {'status_auth': HTTPStatus.CREATED, 'status_create': HTTPStatus.OK}),]
)
@pytest.mark.asyncio
async def test_create_payment(make_post_request, query_data, expected_answer):
    """Так как все сильно завязано на сторонний ресурс,
    то места для маневра очень мало). Чего смогу, то протестирую."""
    body, headers, status = await make_post_request(f'{auth_url}/auth/api/v1/user_crud', query_data['query'])
    logging.error('INFO - %s -- %s', body, status)
    assert status[0] == expected_answer['status_auth']
    user_id = body[0]['id']
    _tariff = query_data['tariff']
    body, headers, status = await make_post_request(f'{create_url}/{user_id}/{_tariff}', {})
    logging.error('INFO - %s', body)
    assert status[0] == expected_answer['status_create']
    assert 'https://yoomoney.ru/checkout/payments/v2/contract' in body[0]

# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [({'query': 'The Star-9', 'page[number]': 0, 'page[size]': 50},
#       {'status': HTTPStatus.OK, 'length': 50, 'api_body': film_list_id_9}),
#      ({'query': 'The Star-9', 'page[number]': 1, 'page[size]': 50},
#       {'status': HTTPStatus.OK, 'length': 10, 'api_body': film_list_id_50}),
#      ({'query': 'The Star-9', 'page[number]': 5, 'page[size]': 10},
#       {'status': HTTPStatus.OK, 'length': 10, 'api_body': film_list_id_50}),
#      ({'query': 'Mashed potato'},
#       {'status': HTTPStatus.NOT_FOUND, 'length': 1, 'api_body': {'detail': 'film not found'}})]
# )
# @pytest.mark.asyncio
# async def test_film_search(make_get_request, query_data, expected_answer):
#     body, headers, status = await make_get_request('films/search/', query_data)
#     body = body if len(body[0]) > 1 else (body,)  # при 404 list.
#     assert status[0] == expected_answer['status']
#     assert len(body[0]) == expected_answer['length']
#     assert body[0][0] == expected_answer['api_body']  # Точное совпадение первое.


# @pytest.mark.parametrize(
#     'query_data, expected_answer',
#     [({'sort': '-imdb_rating', 'page[number]': 0, 'page[size]': 50, 'filter[genre]': '001'},
#       {'status': HTTPStatus.OK, 'length': 50, 'api_body': film_list_id_59}),
#      ({'sort': '-imdb_rating', 'page[number]': 5, 'page[size]': 10, 'filter[genre]': '001'},
#       {'status': HTTPStatus.OK, 'length': 10, 'api_body': film_list_id_9}),
#      ({'filter[genre]': '001'},
#       {'status': HTTPStatus.OK, 'length': 50, 'api_body': film_list_id_0}),
#      ({},
#       {'status': HTTPStatus.OK, 'length': 50, 'api_body': film_list_id_0}),
#      ({'page[number]': 0, 'page[size]': 50, 'filter[genre]': '001'},
#       {'status': HTTPStatus.OK, 'length': 50, 'api_body': film_list_id_0}),
#      ({'sort': '-imdb_rating', 'page[number]': 1, 'page[size]': 50, 'filter[genre]': '001'},
#       {'status': HTTPStatus.OK, 'length': 10, 'api_body': film_list_id_9}),
#      ({'sort': '-imdb_rating', 'page[number]': 0, 'page[size]': 50, 'filter[genre]': '003'},
#       {'status': HTTPStatus.NOT_FOUND, 'length': 1, 'api_body': {'detail': 'film not found'}})]
# )
# @pytest.mark.asyncio
# async def test_films_list(make_get_request, query_data, expected_answer):
#     body, headers, status = await make_get_request('films/', query_data)
#     body = body if len(body[0]) > 1 else (body,)  # При 404 list.
#     assert status[0] == expected_answer['status']
#     assert len(body[0]) == expected_answer['length']
#     assert body[0][0] == expected_answer['api_body']


# @pytest.mark.asyncio
# async def test_cache(make_get_request, get_redis_by_key):
#     """Поверяем кеш. Так как кешируем ответ из ES с помощью
#     - fastapi-cache2[redis]==0.1.9, то не имеем прямого доступа к ключам,
#     так как тесты ассинхронные - то получить их проблематично,
#     в синхроном тесте можно было бы их получить примерно так:
#     def get_redis(redis_client: Redis):
#         redis_keys = await redis_client.scan(_type='string')
#         redis: str = await redis_client.get(redis_keys[1][0])
#         redis: dict = json.loads(redis_keys)
#         return redis
#     Можно конечно получить все ключи, по ним получить весь кеш,
#     и посмотреть наличие, во всем кеше, необходимого запроса,
#     но это такое, так как поля в ES(=кеш) и API endpoint различаются -
#     id=uuid, rating=imdb_rating, genre - вообще list[dict] vs list[str].
#     upd. Попытаюсь встаки сравнить контент Redis/ES vs API endpoint.
#     upd. Добавил отдельный, синхронный тест кеша с проверкой контента.
#     """
#     body, headers, status = await make_get_request('films/', {})
#     # Ключ в Redis постоянен для каждого уникального HTTP запроса,
#     # точнее, в нашем случае, для параметров кешируемой функции запроса к ES.
#     # from fastapi_cache.key_builder import default_key_builder
#     redis: tuple = await get_redis_by_key('fastapi-cache::26e0cf4deac5b61229228b3d633a5534')
#     # Формируем данные из Redis(ES), в идентичную форму данных для ручки.
#     redis_for_eq = [({'uuid': obj['_source']['id'],
#                       'title': obj['_source']['title'],
#                       'imdb_rating': float(obj['_source']['rating'])})
#                     for obj in redis['hits']['hits']]
#     assert status[0] == HTTPStatus.OK
#     assert len(redis) != 0  # Проверяем что в редисе создалась хотябы 1-а запись.
#     # Проверку ниже, я сам прикручу для ваших тестов.
#     assert redis_for_eq == body[0]  # Сравниваем данные Redis c endpoint.
