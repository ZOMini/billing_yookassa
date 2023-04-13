import json
import logging

import aiohttp
import pytest
from aioredis import Redis

# from elasticsearch import AsyncElasticsearch
# from functional.settings import test_settings as TS
# from functional.testdata.es_data_film import films_list
# from functional.testdata.es_data_genre import genres_list
# from functional.testdata.es_data_person import persons_list

# @pytest.fixture(scope='session')
# def get_es_bulk_query():
#     def inner(data: list[dict], index: str, id_field: str) -> list:
#         bulk_query = []
#         for row in data:
#             bulk_query.extend([
#                 json.dumps({'index': {'_index': index, '_id': row[id_field]}}),
#                 json.dumps(row)
#             ])
#         return bulk_query
#     return inner


# @pytest.fixture(scope='session')
# def es_write_data(es_client: AsyncElasticsearch, get_es_bulk_query):
#     async def inner(data: list[dict], es_index: str):
#         bulk_query = get_es_bulk_query(data, es_index, TS.es_id_field)
#         str_query = '\n'.join(bulk_query) + '\n'
#         response = await es_client.bulk(str_query, refresh=True)
#         if response['errors']:
#             raise Exception('Ошибка записи данных в Elasticsearch')
#     return inner


@pytest.fixture
def make_get_request(ahttp_client: aiohttp.ClientSession):
    async def inner(url: str):
        async with ahttp_client.get(url) as response:
            body = await response.json(),
            headers = response.headers,
            status = response.status,
            return body, headers, status
    return inner

@pytest.fixture
def make_post_request(ahttp_client: aiohttp.ClientSession):
    async def inner(url: str, data: dict):
        async with ahttp_client.post(url, json=data) as response:
            body = await response.json(),
            headers = response.headers,
            status = response.status,
            return body, headers, status
    return inner

@pytest.fixture
def get_redis_by_key(redis_client: Redis):
    async def inner(key: str = '') -> tuple:
        redis: str = await redis_client.get(key)
        redis: tuple = json.loads(redis)
        return redis
    return inner


@pytest.fixture
def get_redis_keys(redis_client: Redis):
    # Не используестя, но нужна для разработки.
    async def inner(key: str = None) -> dict:
        redis_keys = await redis_client.scan(_type='string')
        return redis_keys
    return inner


@pytest.fixture
async def clear_redis(redis_client: Redis):
    await redis_client.flushall()


# @pytest.fixture(scope="session", autouse=True)
# async def load_es_data(es_write_data):
#     await es_write_data(films_list, 'movies')
#     await es_write_data(genres_list, 'genres')
#     await es_write_data(persons_list, 'persons')
