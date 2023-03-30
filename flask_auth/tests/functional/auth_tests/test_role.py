import logging
from http import HTTPStatus

import pytest

from tests.functional.utils.api_utils import (
    make_get_request,
    make_put_request,
    make_post_request,
    make_delete_request
)

from tests.functional.test_data.api_users import (
    user_admin,
    user_delete_role,
    user_new_role
)


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.OK}),]
)
@pytest.mark.asyncio
async def test_get_roles(session,user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    user_name = user['name']
    body, headers, status = await make_get_request(
        session=session,
        prefix=f'/get_user_roles/{user_name}',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']



@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.CREATED}),]
)
@pytest.mark.asyncio
async def test_add_roles(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    data = {"user":"user_new_role", "role":"admin"}
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/add_role_for_user',
        headers={'Authorization': f'Bearer {token}'} if token else None, data=data)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.NO_CONTENT}),]
)
@pytest.mark.asyncio
async def test_delete_roles(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    data = {"user":"user_delete_role", "role":"admin"}
    body, headers, status = await make_delete_request(
        session=session,
        prefix=f'/delete_role_from_user',
        headers={'Authorization': f'Bearer {token}'} if token else None, data=data)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.CREATED}),]
)
@pytest.mark.asyncio
async def test_role_add(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    data = {"role" : "admin2"}
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/role_crud',
        headers={'Authorization': f'Bearer {token}'} if token else None,
        data=data)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.CREATED}),]
)
@pytest.mark.asyncio
async def test_role_update(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    data = {"old_role" : "admin2", "new_role": "admin3"}
    body, headers, status = await make_put_request(
        session=session,
        prefix=f'/role_crud',
        headers={'Authorization': f'Bearer {token}'} if token else None,
        data=data)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.CREATED}), ]
)
@pytest.mark.asyncio
async def test_role_delete(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    data = {"role": "admin2"}
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/role_crud',
        headers={'Authorization': f'Bearer {token}'} if token else None,
        data=data)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_admin, {'status': HTTPStatus.OK}),]
)
@pytest.mark.asyncio
async def test_role_get(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    body, headers, status = await make_get_request(
        session=session,
        prefix=f'/role_crud',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']
