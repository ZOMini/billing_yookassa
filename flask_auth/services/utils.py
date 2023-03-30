import logging
import secrets
import string
from datetime import datetime, timedelta
from functools import wraps
from http import HTTPStatus as HTTP
from zlib import crc32

from flask import jsonify, request
from flask_jwt_extended import get_jwt

from core.config import ACCESS_EXPIRES, REFRESH_EXPIRES, TESTS, THROTTLING
from db.redis import jwt_redis_blocklist


def role_required(*req_roles: str):
    '''Декоратор только для запросов с JWT. Дополняет jwt_required,
    проверяет доступность по роли.
    Если роль superuser то доступны все ручки.'''
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            claims = get_jwt()
            for req_role in req_roles:
                if req_role in claims['roles'] or 'superuser' in claims['roles']:
                    return fn(*args, **kwargs)
            else:
                return jsonify(msg='The role does not grant access! Or refresh you access token!'), HTTP.FORBIDDEN
        return decorator
    return wrapper


def token_expire_time(access: bool, token_time: datetime) -> timedelta | None:
    '''Вычисляет оставшееся время токена, если минус возвращает None,
    значит отзывать не нужно, токен уже не валидный.'''
    if access:
        expire = ACCESS_EXPIRES - (datetime.utcnow() - token_time)
    elif not access:
        expire = REFRESH_EXPIRES - (datetime.utcnow() - token_time)
    if expire < timedelta():
        return None
    return expire


def user_agent_hash(user_agent: str) -> int:
    '''Функция хеширует user_agent, чтобы уменьшить размер,
    используем crc32 для скорости.'''
    return crc32(user_agent.encode('utf-8'))


def check_user_agent():
    '''Декоратор сверяет user_agent текущий, с получившим токен.
    Если не совпадают, то 403.
    Можно использовать везде - где токен, но поставлю на оба logout'а, и refresh.
    Если использовать везде, то правильнее воспользоваться этой механикой:
    https://flask-jwt-extended.readthedocs.io/en/stable/api/#module-flask_jwt_extended '''
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            jwt = get_jwt()
            if user_agent_hash(request.headers.get('User-Agent', '')) == jwt['ua']:
                return fn(*args, **kwargs)
            else:
                return jsonify(msg='The keys were received by another user_agent'), HTTP.FORBIDDEN
        return decorator
    return wrapper


def throttling_user_agent(*req_roles: str):
    '''Декоратор не влияет на admin и superuser и указаных в param.
    Остальных 'душит' помещаяя в Redis.
    Дополняет jwt_required где это нужно, но и пустит без авторизации.'''
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            try:
                # Не тротлит если staff или в env - TESTS = True.
                if TESTS:
                    return fn(*args, **kwargs)
                jwt = get_jwt()
                if 'superuser' in jwt['roles'] or 'admin' in jwt['roles']:
                    return fn(*args, **kwargs)
                elif req_roles:
                    for role in req_roles:
                        if role in jwt['roles']:
                            return fn(*args, **kwargs)
                raise Exception
            except Exception:
                hash_u_a = user_agent_hash(request.headers.get('User-Agent', 'empty'))
                ip = request.remote_addr
                if jwt_redis_blocklist.get(str(hash_u_a) + ip) is None:
                    jwt_redis_blocklist.set(str(hash_u_a) + ip, "", THROTTLING)
                    return fn(*args, **kwargs)
                else:
                    return jsonify(msg='Try again later'), HTTP.FORBIDDEN
        return decorator
    return wrapper


def generate_password(length):
    letters_and_digits = string.ascii_letters + string.digits
    crypt_rand_string = ''.join(secrets.choice(
        letters_and_digits) for i in range(length))
    return crypt_rand_string
