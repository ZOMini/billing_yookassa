import json

import aiohttp
import pytest
from aioredis import Redis

from tests.functional.settings import test_settings as TS


async def make_get_request(session: aiohttp.ClientSession, prefix: str, params: dict = None, headers: dict = None):
    url = f"{TS.service_url}{prefix}"
    async with session.get(url, params=params, headers=headers) as response:
        body = await response.json(),
        headers = response.headers,
        status = response.status,
        return body, headers, status


async def make_delete_request(session: aiohttp.ClientSession, prefix: str, data: dict = None, headers: dict = None):
    url = f"{TS.service_url}{prefix}"
    async with session.delete(url, json=data, headers=headers) as response:
        body = await response.json(),
        headers = response.headers,
        status = response.status,
        return body, headers, status


async def make_post_request(session: aiohttp.ClientSession, prefix: str, data: dict = None, headers: dict = None):
    url = f"{TS.service_url}{prefix}"
    async with session.post(url, json=data, headers=headers) as response:
        body = await response.json(),
        headers = response.headers,
        status = response.status,
        return body, headers, status


async def make_put_request(session: aiohttp.ClientSession, prefix: str, data: dict = None, headers: dict = None):
    url = f"{TS.service_url}{prefix}"
    async with session.put(url, json=data, headers=headers) as response:
        body = await response.json(),
        headers = response.headers,
        status = response.status,
        return body, headers, status


async def get_redis_by_key(redis_client: Redis, key: str = '') -> tuple:
    redis: str = await redis_client.get(key)
    redis: tuple = json.loads(redis)
    return redis


async def clear_redis(redis_client: Redis):
    await redis_client.flushall()

