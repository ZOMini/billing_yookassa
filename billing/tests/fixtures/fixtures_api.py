import http
import json
import logging

import aiohttp
import pytest
import pytest_asyncio
from aioredis import Redis
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import select

from models.models_pg import PaymentPG, Tariff, UserStatus
from tests.test_settings import auth_create_url, auth_get_id_url, create_url
from tests.testdata.api_data import tariff_dict, tariff_id, user_create_data


@pytest_asyncio.fixture
def make_get_request(ahttp_client: aiohttp.ClientSession):
    async def inner(url: str, query: dict):
        async with ahttp_client.get(url, params=query) as response:
            body = await response.json(),
            headers = response.headers,
            status = response.status,
            return body, headers, status
    return inner


@pytest_asyncio.fixture
def make_post_request(ahttp_client: aiohttp.ClientSession):
    async def inner(url: str, query: dict, data: dict):
        async with ahttp_client.post(url, params=query, json=data) as response:
            body = await response.json(),
            headers = response.headers,
            status = response.status,
            return body, headers, status
    return inner


@pytest_asyncio.fixture
def get_redis_by_key(redis_client: Redis) -> tuple:
    async def inner(key: str = '') -> tuple:
        redis: str = await redis_client.get(key)
        redis: tuple = json.loads(redis)
        return redis
    return inner


@pytest_asyncio.fixture
def get_redis_keys(redis_client: Redis):
    async def inner(key: str = None) -> dict:
        redis_keys = await redis_client.scan(_type='string')
        return redis_keys
    return inner


@pytest_asyncio.fixture(scope="session", autouse=True)
async def clear_redis(redis_client: Redis):
    await redis_client.flushall()


@pytest_asyncio.fixture()
async def clear_pg(pg_client: AsyncSession) -> None:
    scalars = await pg_client.scalars(select(UserStatus))
    for scalar in scalars:
        await pg_client.delete(scalar)
    scalars = await pg_client.scalars(select(PaymentPG))
    for scalar in scalars:
        await pg_client.delete(scalar)
    await pg_client.commit()


@pytest.fixture(scope='session')
def pg_write_data(pg_client: AsyncSession):
    async def inner(obj: Tariff | UserStatus, data: dict):
        pg_obj = obj(**data)
        pg_client.add(pg_obj)
        await pg_client.commit()
        return pg_obj.id
    return inner


@pytest.fixture(scope='session')
def pg_write_payment_data(pg_client: AsyncSession) -> PaymentPG:
    async def inner(obj: PaymentPG, data: dict, tariff: Tariff, userstatus: UserStatus):
        pg_obj: PaymentPG = obj(**data, tariff=tariff, userstatus=userstatus)
        pg_client.add(pg_obj)
        await pg_client.commit()
        return pg_obj
    return inner


@pytest_asyncio.fixture()
async def get_or_create_user(make_post_request, make_get_request) -> str:
    body, headers, status = await make_post_request(auth_create_url, {}, user_create_data)
    if status[0] == http.HTTPStatus.BAD_REQUEST:
        body, headers, status = await make_get_request(auth_get_id_url, {'username': 'testuser'})
    return body[0]['user_id']


@pytest_asyncio.fixture()
def pg_get_obj_by_id(pg_client: AsyncSession):
    async def inner(obj: Tariff | UserStatus | PaymentPG, id: str):
        await pg_client.flush()
        pg_obj = await pg_client.get(obj, id)
        await pg_client.commit()
        await pg_client.flush()
        return pg_obj
    return inner
