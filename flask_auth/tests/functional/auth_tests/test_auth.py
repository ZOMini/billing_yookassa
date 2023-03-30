import json
import logging
from http import HTTPStatus

import pytest

from tests.functional.test_data.api_users import (
    user_bad_token,
    user_change_pwd,
    user_change_pwd2_missing,
    user_change_wrong_pwd,
    user_change_wrong_username,
    user_expired_token,
    user_good_token,
    user_login,
    user_login_wrong_pwd,
    user_login_wrong_user,
    user_logout,
    user_logout_wrong_token,
    user_new,
    user_new_existing,
    user_new_pwd2_missing,
    user_new_pwd_mismatch,
    user_new_pwd_missing,
    user_no_token,
    user_refresh
)
from tests.functional.utils.api_utils import (
    make_delete_request,
    make_get_request,
    make_post_request,
    make_put_request
)


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_good_token, {'status': HTTPStatus.OK}),
     (user_bad_token, {'status': HTTPStatus.UNPROCESSABLE_ENTITY}),]
)
@pytest.mark.asyncio
async def test_history(session, user, expected_answer):
    token = user['token']
    if not len(token):
        body, headers, status = await make_post_request(
            session=session,
            prefix=f'/login',
            data=user)
        token = body[0]['access_token']
    body, headers, status = await make_get_request(
        session=session,
        prefix=f'/history_auth',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_new, {'status': HTTPStatus.CREATED}),
    (user_new_pwd_mismatch, {'status': HTTPStatus.BAD_REQUEST}),
    (user_new_pwd2_missing, {'status': HTTPStatus.BAD_REQUEST}),
    (user_new_existing, {'status': HTTPStatus.BAD_REQUEST}),]
)
@pytest.mark.asyncio
async def test_create(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/user_crud',
        data=user)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_change_pwd, {'status': HTTPStatus.ACCEPTED}),
    (user_change_wrong_pwd, {'status': HTTPStatus.UNAUTHORIZED}),
    (user_change_wrong_username, {'status': HTTPStatus.FORBIDDEN}),
    (user_change_pwd2_missing, {'status': HTTPStatus.FORBIDDEN}),]
)
@pytest.mark.asyncio
async def test_change_pwd(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token'] if user['name'] == 'user_change_pwd' else None
    body, headers, status = await make_put_request(
        session=session,
        prefix=f'/user_crud',
        data=user,
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_new, {'status': HTTPStatus.OK}),
     (user_login_wrong_pwd, {'status': HTTPStatus.UNAUTHORIZED}),
     (user_login_wrong_user, {'status': HTTPStatus.UNAUTHORIZED}),]
)
@pytest.mark.asyncio
async def test_login(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_logout, {'status': HTTPStatus.OK}),]
)
@pytest.mark.asyncio
async def test_logout(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    body, headers, status = await make_delete_request(
        session=session,
        prefix=f'/logout',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_logout, {'status': HTTPStatus.OK}),]
)
@pytest.mark.asyncio
async def test_logout_all(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['access_token']
    body, headers, status = await make_delete_request(
        session=session,
        prefix=f'/logout_all',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']


@pytest.mark.parametrize(
    'user, expected_answer',
    [(user_refresh, {'status': HTTPStatus.CREATED}),]
)
@pytest.mark.asyncio
async def test_refresh(session, user, expected_answer):
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/login',
        data=user)
    token = body[0]['refresh_token']
    body, headers, status = await make_post_request(
        session=session,
        prefix=f'/refresh',
        headers={'Authorization': f'Bearer {token}'} if token else None)
    assert status[0] == expected_answer['status']

