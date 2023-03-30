from datetime import timedelta

import pika
from flask import Flask
from flask_jwt_extended import JWTManager
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    EXCHANGE = Field('notifications')
    INSTANT_QUEUE = Field('instant_events')
    ROUTING_KEY = Field('instant_events')
    RABBIT_USER = Field('auth_publisher')
    RABBIT_PASS = Field('qweqwe')
    RABBIT_HOST = Field('localhost')
    
    POSTGRES_DB: str = Field(...)
    POSTGRES_USER: str = Field(...)
    POSTGRES_PASSWORD: str = Field(...)
    POSTGRES_HOST: str = Field(...)
    DB_DOCKER_HOST: str = Field(...)
    POSTGRES_PORT: int = Field(...)

    REDIS_HOST: str = Field(...)
    REDIS_PORT: int = Field(...)
    REDIS_URL: str = Field(...)

    FLASK_SECRET_KEY: str = Field(...)
    JWT_SECRET_KEY: str = Field(...)
    JWT_ACCESS_TOKEN_EXPIRES: int = Field(...)  # Часов
    JWT_REFRESH_TOKEN_EXPIRES: int = Field(...)  # Дней
    THROTTLING: int = Field(...)  # Секунд
    SALT_PASSWORD: str = Field(...)
    SUPERUSER_NAME: str = Field(...)
    SUPERUSER_EMAIL: str = Field(...)
    SUPERUSER_PASSWORD: str = Field(...)

    DEBUG: bool = Field(False)
    TESTS: bool = Field(False)
    DEVELOP: bool = Field(False)
    EXT_LOGGING: bool = Field(False)

    YANDEX_CLIENT_ID: str = Field(None)
    YANDEX_CLIENT_SECRET: str = Field(None)
    YANDEX_ACCESS_TOKEN_URL: str = Field('https://oauth.yandex.ru/token')
    YANDEX_AUTHORIZE_URL: str = Field('https://oauth.yandex.ru/authorize')
    YANDEX_API_BASE_URL: str = Field('https://login.yandex.ru/info')
    YANDEX_USERINFO_URL: str = Field('https://login.yandex.ru/info?format=json')
    YANDEX_UNSUBSCRIBE_PAGE: str = Field('https://passport.yandex.ru/profile/access')

    VK_CLIENT_ID: str = Field(None)
    VK_CLIENT_SECRET: str = Field(None)
    VK_ACCESS_TOKEN_URL: str = Field('https://oauth.vk.com/access_token')
    VK_AUTHORIZE_URL: str = Field('https://oauth.vk.com/authorize')
    VK_API_BASE_URL: str = Field('https://api.vk.com/method')
    VK_USERINFO_URL: str = Field('https://api.vk.com/method/users.get?v=5.131')
    VK_UNSUBSCRIBE_PAGE: str = Field('https://vk.com/settings?act=apps')

    JAEGER_HOST: str = Field('jaeger')
    JAEGER_PORT: str = Field('6831')


    GOOGLE_CLIENT_ID: str = Field(None)
    GOOGLE_CLIENT_SECRET: str = Field(None)
    GOOGLE_ACCESS_TOKEN_URL: str = Field('https://www.googleapis.com/oauth2/v4/token')
    GOOGLE_AUTHORIZE_URL: str = Field('https://accounts.google.com/o/oauth2/v2/auth')
    GOOGLE_API_BASE_URL: str = Field('https://www.googleapis.com/oauth2/v2/')
    GOOGLE_USERINFO_URL : str = Field('https://www.googleapis.com/oauth2/v2/userinfo')
    GOOGLE_UNSUBSCRIBE_PAGE : str = Field('https://accounts.google.com/o/oauth2/revoke')

    logstash_host: str = Field(...)
    logstash_port: int = Field(...)
    log_level: str = Field('INFO')
    
    notif_api_url: str = Field('http://api_notif:8201')

    class Config:
        env_file = './.env'
        env_file_encoding = 'utf-8'


settings = Settings()

ACCESS_EXPIRES = timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRES)
REFRESH_EXPIRES = timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES)
THROTTLING = timedelta(seconds=settings.THROTTLING)
TESTS = settings.TESTS

app = Flask('auth_api')
app.config['DEBUG'] = settings.DEBUG
app.config['SECRET_KEY'] = settings.FLASK_SECRET_KEY
app.config['JWT_SECRET_KEY'] = settings.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = ACCESS_EXPIRES
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = REFRESH_EXPIRES
jwt = JWTManager(app)

credentials = pika.PlainCredentials(username=settings.RABBIT_USER, password=settings.RABBIT_PASS)

def rabbit_conn(credentials=credentials):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=settings.RABBIT_HOST, credentials=credentials))
    return connection
