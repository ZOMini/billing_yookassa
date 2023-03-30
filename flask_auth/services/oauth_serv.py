import logging
from http import HTTPStatus as HTTP

from authlib.integrations.flask_client import FlaskOAuth2App, OAuth
from flask import Response, current_app, jsonify, request
from models.db_models import Auth, User
from pydantic import BaseModel
from werkzeug.exceptions import BadRequest, NotFound

from core.config import settings
from db.db import db_session
from services.models_serv import AuthServ, UserServ
from services.notif_serv import notif_send
from services.utils import generate_password


class SocialUserModel(BaseModel):
    username: str = ''
    email: str = ''


class OauthServ:

    @classmethod
    def get_oauth(cls) -> OAuth:
        return current_app.extensions['authlib.integrations.flask_client']

    @classmethod
    def check_source(cls) -> FlaskOAuth2App:
        '''Метод проверяет наличее регистрации провайдера в core.oauth,
        возвращает настройки этого провайдера, в виде FlaskOAuth2App
        приложения.'''
        oauth = cls.get_oauth()
        try:
            provider = request.args['provider']
            oauth = getattr(oauth, provider)
        except AttributeError:
            raise NotFound('Unknown provider name')
        except KeyError:
            raise BadRequest('None provider name')
        return oauth

    @classmethod
    def get_user_info(cls, oauth_app: FlaskOAuth2App) -> SocialUserModel:
        '''Метод принимает приложение FlaskOAuth2App с полученными ключами,
        возвращает данные пользователя от провайдера.'''
        # По сути нам нужен только email и username.
        # В теории говорилось что где-то нет username'а,
        # можно использовать email как имя например.
        if oauth_app.name == 'yandex':
            userinfo = oauth_app.get(settings.YANDEX_USERINFO_URL)
            userinfo_dict: dict = userinfo.json()
            logging.error('-----userinfo_dict----- %s', userinfo_dict)
            return SocialUserModel(username=userinfo_dict.get('login'),
                                   email=userinfo_dict.get('default_email'))
        elif oauth_app.name == 'vk':
            userinfo = oauth_app.get(settings.VK_USERINFO_URL)
            logging.error('-----tokeninfo----- %s', oauth_app.token)
            logging.error('-----tokeninfo_email----- %s', oauth_app.token.get('email'))
            userinfo_dict = userinfo.json()['response'][0]
            logging.error('-----userinfo_dict----- %s', userinfo_dict)
            return SocialUserModel(username=userinfo_dict.get('first_name') + '_'
                                   + userinfo_dict.get('last_name') + '-'
                                   + str(userinfo_dict.get('id')),
                                   email=oauth_app.token.get('email'))
        elif oauth_app.name == 'google':
            userinfo = oauth_app.get(settings.GOOGLE_USERINFO_URL)
            userinfo_dict: dict = userinfo.json()
            logging.error('-----userinfo_dict----- %s', userinfo_dict)
            return SocialUserModel(username=userinfo_dict.get('email'),
                                   email=userinfo_dict.get('email'))

    @classmethod
    def check_and_create_account(cls, oauth_app: FlaskOAuth2App) -> tuple[Response, HTTP]:
        '''Метод проверяет есть ли пользователь в базе, если нет - создает,
        возращает пару токенов для стандартного логина.
        Вся движуха расчитана на уникальность email'a, так же расчет на то,
        что если емаил есть в соцсети то он прошел валидацию и user его
        подтвердил.'''
        user_info = OauthServ.get_user_info(oauth_app)
        user = UserServ.get_obj_by_name(user_info.email, True)
        if not user:
            try:
                # password отдельно в переменную для письма, тк в модели хеш.
                password = generate_password(16)
                # name в таком варианте должен быть уникальным.
                user = User(user_info.username + '_from_' + oauth_app.name,
                            user_info.email,
                            password)
                db_session.add(user)
                db_session.commit()
                # Тут отправляем письмо, видимо как дойдем до отложенных задач.
                # notif_send(user.name, user.email, user.id)
                logging.error('INFO %s created - email sent.', user)
            except Exception as e:
                db_session.rollback()
                return jsonify(err=e.args), HTTP.BAD_REQUEST
        return AuthServ.login_refresh_service(user, True)
