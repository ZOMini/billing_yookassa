import asyncio
import json
import logging
from datetime import datetime
from http import HTTPStatus as HTTP
from typing import Any

from flask import Response, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    verify_jwt_in_request
)
from sqlalchemy import and_

from core.config import rabbit_conn
from core.config import settings as SETT
from db.db import db_session
from db.redis import jwt_redis_blocklist
from models.db_models import Auth, Role, User
from services.notif_serv import notif_send
from services.utils import token_expire_time, user_agent_hash


class UserServ(User):

    @classmethod
    def get_obj_by_name(cls, name: str, email: bool = False) -> 'User':
        '''Отдает обект по имени. Опционально по емайлу.'''
        if email:
            return db_session.query(User).filter(User.email == name).one_or_none()
        return db_session.query(User).filter(User.name == name).one_or_none()

    @classmethod
    def get_obj_by_id(cls, id: str) -> 'User':
        '''Отдает обект по id.'''
        return db_session.query(User).filter(User.id == id).one_or_none()

    @classmethod
    def create_user(cls, name: str, email: str, password: str, password2: str) -> tuple[Response, HTTP]:
        '''Создаем User.'''
        if password == password2 and len(password) >= 8:
            try:
                user = User(name=name,
                            email=email,
                            password=password)
                db_session.add(user)
                db_session.commit()
                # notif_send(user.name, user.email, user.id)
                try:
                    body = {'user_id': str(user.id), 'user_name': user.name, 'user_email': user.email, 'event_type': 'user_create'}
                    connection = rabbit_conn()
                    channel = connection.channel()
                    channel.basic_publish(SETT.EXCHANGE, SETT.ROUTING_KEY, json.dumps(body))
                    logging.error('RABBIT AUTH - OK')
                    connection.close()
                except Exception as e:
                    logging.error('RABBIT AUTH ERROR - %s', e)
                return jsonify(msg='User created. Login is email.', id = user.id), HTTP.CREATED
            except Exception as e:
                db_session.rollback()
                return jsonify(msg="Wrong email or password or name",
                               err=e.args), HTTP.BAD_REQUEST
        else:
            return jsonify('password != password2 or length < 8'), HTTP.BAD_REQUEST

    @classmethod
    def update_user(cls, name: str, email: str, pass_old: str, password: str, password2: str) -> tuple[Response, HTTP]:
        '''Изменяем User'''
        try:
            user = cls.get_obj_by_name(name)
            user.email = email if email else user.email
            pass_old_hash = user.password_hash(pass_old, user.email)
            if user.password == pass_old_hash and password and password2:
                if password == password2 and len(password) >= 8:
                    user.password = user.password_hash(password, user.email)
                    db_session.add(user)
                    db_session.commit()
                    try:
                        body = {'user_id': str(user.id), 'user_name': user.name, 'user_email': user.email, 'event_type': 'change_password'}
                        connection = rabbit_conn()
                        channel = connection.channel()
                        channel.basic_publish(SETT.EXCHANGE, SETT.ROUTING_KEY, json.dumps(body))
                        logging.error('RABBIT AUTH UPD - OK')
                        connection.close()
                    except Exception as e:
                        logging.error('RABBIT AUTH UPD ERROR - %s', e)
                    return jsonify('User update.'), HTTP.ACCEPTED
                else:
                    return jsonify('password != password2 or length < 8'), HTTP.BAD_REQUEST
            raise Exception
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong email or password or name",
                           err=e.args), HTTP.BAD_REQUEST

    @classmethod
    def user_crud(cls) -> tuple[Response, HTTP]:
        name = request.json.get('name', None)
        email = request.json.get('email', None)
        pass_old = request.json.get('pass_old', None)
        password = request.json.get('password', None)
        password2 = request.json.get('password2', None)
        if request.method == 'POST':
            response = cls.create_user(name, email, password, password2)
        elif request.method == 'PUT':
            verify_jwt_in_request()
            user = get_current_user()
            json = request.get_json()
            if user.name != json['name']:
                return jsonify('Token not for this user.'), HTTP.UNAUTHORIZED
            response = cls.update_user(name, email, pass_old, password, password2)
        else:
            response = jsonify(), HTTP.METHOD_NOT_ALLOWED
        return response

    @classmethod
    def get_user_roles(cls, username: str) -> tuple[Response, HTTP]:
        '''Отдает лист ролей пользователя.'''
        user = cls.get_obj_by_name(username)
        if user is None:
            return jsonify('No user'), HTTP.NOT_FOUND
        list_roles = [item.role for item in user.role]
        if not list_roles:
            return jsonify('No roles'), HTTP.NOT_FOUND
        return jsonify({'roles': list_roles}), HTTP.OK

    @classmethod
    def add_or_del_role_user(cls, json: dict, add: bool = False) -> tuple[Response, HTTP]:
        '''Метод добавляет или удаляет роль пользователя.
        Добавляет все ключи в блоклист, при удалении. На выходе готовый Response.'''
        try:
            role = RoleServ.get_obj_by_role(json['role'])
            user = cls.get_obj_by_name(json['user'])
            if add:
                user.role.append(role)
                db_session.commit()
                return jsonify('Role added for user. Refresh user access token.'), HTTP.CREATED
            else:
                user.role.remove(role)
                user_agents = db_session.query(Auth.user_agent).filter(Auth.user_id == str(user.id)).distinct().all()
                for user_agent in user_agents:
                    AuthServ.add_old_tokens_in_block(user, user_agent_hash(user_agent[0]))
                    last_auth = AuthServ.last_auth(user.id, user_agent_hash(user_agent[0]))
                    last_auth.access_token = None
                    last_auth.refresh_token = None
                db_session.commit()
                return jsonify('Remove a role from a user. All keys have been revoked'), HTTP.NO_CONTENT
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong role.id and user.id or see in err",
                           err=e.args), HTTP.BAD_REQUEST


    @classmethod
    def add_or_del_role_user_billing(cls, json: dict, add: bool = False) -> tuple[Response, HTTP]:
        '''Метод специально для биллинга. Метод добавляет или удаляет роль пользователя.
        Добавляет все ключи в блоклист, в обоих случаях. На выходе готовый Response.'''
        try:
            role = RoleServ.get_obj_by_role(json['role'])
            user = cls.get_obj_by_id(json['user'])
            logging.error('DDDDDDDDDDDDDDDDDDD - %s -- %s', role.role, user.id)
            user_agents = db_session.query(Auth.user_agent).filter(Auth.user_id == str(user.id)).distinct().all()
            for user_agent in user_agents:
                AuthServ.add_old_tokens_in_block(user, user_agent_hash(user_agent[0]))
                last_auth = AuthServ.last_auth(user.id, user_agent_hash(user_agent[0]))
                last_auth.access_token = None
                last_auth.refresh_token = None
            if add:
                user.role.append(role)
                db_session.commit()
                return jsonify('Role added for user. Refresh user access token.'), HTTP.CREATED
            user.role.remove(role)
            db_session.commit()
            return jsonify('Remove a role from a user. All keys have been revoked'), HTTP.NO_CONTENT
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong role.id and user.id or see in err",
                           err=e.args), HTTP.BAD_REQUEST


class AuthServ(Auth):

    @classmethod
    def registry_auth(cls, user: User,
                      user_agent: str | None = None,
                      u_a_hash: int | None = None,
                      access_token: str | None = None,
                      refresh_token: str | None = None):
        '''Метод создает новую запись в Auth.'''
        auth = cls(user_id=str(user.id),
                   user_agent=user_agent,
                   u_a_hash=u_a_hash,
                   access_token=access_token,
                   refresh_token=refresh_token)
        db_session.add(auth)
        db_session.commit()

    @classmethod
    def history_auth(cls, user_id: str, page: int, size: int) -> list[list[str]]:
        ''' Метод формирует список авторизаций
        текущего пользователя через /login.
        Можно было через репр формировать, но вот так:)'''
        user_list = [[datetime.isoformat(item.data_time), item.user_agent] for item in db_session.query(cls).filter(cls.user_id == user_id).order_by(cls.data_time.desc())[page * size:page * size + size]]
        return user_list

    @classmethod
    def last_auth(cls, user_id: str, u_a_hash: int) -> 'Auth':
        '''Метод отдает последнюю авторизацию по id пользователя и user_agent.'''
        if last_auth := db_session.query(cls).filter(and_(cls.user_id == str(user_id), cls.u_a_hash == u_a_hash)).order_by(cls.data_time.desc()).first():
            return last_auth
        return None

    @classmethod
    def tokens_from_db(cls, user_id: str, u_a_hash: int) -> tuple[Any, Any, Any]:
        '''Метод возвращает пару токенов ACCESS/REFRESH
        и время их последнего обновления, из последней сессии Auth.'''
        # Upd. Добавил user_agent для отбора нужных для отзыва ключей.
        if token := db_session.query(cls.access_token, cls.refresh_token, cls.tokens_time).filter(and_(cls.user_id == str(user_id), cls.u_a_hash == u_a_hash)).order_by(cls.data_time.desc()).first():
            return token[0], token[1], token[2]
        return None, None, None

    @classmethod
    def add_old_tokens_in_block(cls, user: User, u_a_hash: int) -> None:
        '''Метод добавляет пару токенов в блоклист Redis.'''
        # Так как мы не храним в DB время жизни JWT(это увеличит нагрузку на базу),
        # то блоклистим токены на максимально возможный срок их жизни.
        # UPD. Добавил в Auth поле даты последней выдачи ключей, теперь старые ключи
        # отзываются на ОСТАВШИЙСЯ срок их жизни.
        access_token, refresh_token, tokens_time = cls.tokens_from_db(user.id, u_a_hash)
        if access_token:
            expire_time = token_expire_time(True, tokens_time)
            if expire_time:
                jwt_redis_blocklist.set(access_token, "", ex=expire_time)
        if refresh_token:
            expire_time = token_expire_time(False, tokens_time)
            if expire_time:
                jwt_redis_blocklist.set(refresh_token, "", ex=expire_time)

    @classmethod
    def login_refresh_service(cls, user: User, login: bool = False) -> tuple[str, str]:
        '''Метод для login/refresh endpoints.
        При логине: создает новую пару токенов, добавляет запись в журнал Auth,
        добавляет старые ключи(для user_agent) в блоклист.
        При рефреше: то же самое, но изменяет последнюю запись в журнале Auth,
        на новые ключи.
        Вся движуха с учетом user_agent'а от которого запрос.'''
        user_agent = request.headers.get('User-Agent', 'empty')
        u_a_hash = user_agent_hash(user_agent)
        access_token = create_access_token(identity=user)
        refresh_token = create_refresh_token(identity=user)
        decode_access_token = decode_token(access_token)
        decode_refresh_token = decode_token(refresh_token)
        cls.add_old_tokens_in_block(user, u_a_hash)
        if login:
            cls.registry_auth(user=user, user_agent=user_agent,
                              u_a_hash=u_a_hash,
                              access_token=decode_access_token['jti'],
                              refresh_token=decode_refresh_token['jti'])
        else:
            last_auth = cls.last_auth(user.id, u_a_hash)
            last_auth.access_token = decode_access_token['jti']
            last_auth.refresh_token = decode_refresh_token['jti']
            db_session.commit()
        return access_token, refresh_token

    @classmethod
    def logout_service(cls, user: User) -> None:
        '''Изменяет последнюю запись в журнале Auth, заменяя ключи на None.
        Добавляет в блоклист.'''
        user_agent = request.headers.get('User-Agent', 'empty')
        u_a_hash = user_agent_hash(user_agent)
        cls.add_old_tokens_in_block(user, u_a_hash)
        last_auth = cls.last_auth(user.id, u_a_hash)
        last_auth.access_token = None
        last_auth.refresh_token = None
        db_session.commit()

    @classmethod
    def logout_all_service(cls, user: User) -> None:
        '''Отзывает все ключи, всех user_agent'ов, заменяя все ключи на None.
        Добавляет в блоклист ключи для всех user_agent'ов.'''
        u_a_hashes = db_session.query(cls.u_a_hash).filter(cls.user_id == str(user.id)).distinct().all()
        for u_a_hash in u_a_hashes:
            cls.add_old_tokens_in_block(user, u_a_hash[0])
            last_auth = cls.last_auth(user.id, u_a_hash[0])
            last_auth.access_token = None
            last_auth.refresh_token = None
        db_session.commit()


class RoleServ(Role):

    @classmethod
    def get_obj_by_role(cls, role: str) -> 'Role':
        return db_session.query(Role).filter(Role.role == role).one_or_none()

    @classmethod
    def get_list_roles(cls) -> tuple[Response, HTTP]:
        result = [item.role for item in db_session.query(Role).all()]
        if not result:
            return jsonify(msg="Roles are missing"), HTTP.BAD_REQUEST
        return jsonify({'roles': result}), HTTP.OK

    @classmethod
    def create_role(cls) -> tuple[Response, HTTP]:
        json = request.get_json()
        role = Role(role=json['role'])
        try:
            db_session.add(role)
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong role", err=e.args), HTTP.BAD_REQUEST
        return jsonify('Role created.'), HTTP.CREATED

    @classmethod
    def update_role(cls) -> tuple[Response, HTTP]:
        json = request.get_json()
        try:
            role_obj = cls.get_obj_by_role(json['old_role'])
            role_obj.role = json['new_role']
            db_session.add(role_obj)
            db_session.commit()
            return jsonify('Role update.'), HTTP.CREATED
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong role", err=e.args), HTTP.BAD_REQUEST

    @classmethod
    def delete_role(cls) -> tuple[Response, HTTP]:
        json = request.get_json()
        try:
            role = cls.get_obj_by_role(json['role'])
            db_session.delete(role)
            db_session.commit()
            return jsonify('Role delete.'), HTTP.NO_CONTENT
        except Exception as e:
            db_session.rollback()
            return jsonify(msg="Wrong role", err=e.args), HTTP.BAD_REQUEST

    @classmethod
    def role_crud(cls) -> tuple[Response, HTTP]:
        if request.method == 'POST':
            response = cls.create_role()
        elif request.method == 'DELETE':
            response = cls.delete_role()
        elif request.method == 'PUT':
            response = cls.update_role()
        elif request.method == 'GET':
            response = cls.get_list_roles()
        return response
