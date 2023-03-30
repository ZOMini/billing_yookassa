from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    DEFERRED_TIME = '10:30'
    INSTANT_TIME = 5
    AUTH_URL = Field('http://127.0.0.1:5000/auth/api/v1/get_user_by_id')
    POSTGRES_DB = Field("notif_db")
    POSTGRES_USER = Field("app")
    POSTGRES_PASSWORD = Field("123qwe")
    POSTGRES_HOST = Field("127.0.0.1")
    DB_DOCKER_HOST = Field("notif_db")
    POSTGRES_PORT = Field("5432")

    SMTP_HOST = Field("mailhog")  #  "smtp.mail.ru"
    SMTP_PORT = Field(1025)  #  "465"
    SMTP_USER = Field("qqwwaa@mail.ru")
    SMTP_PASSWORD = Field("")

    EXCHANGE = Field('notifications')
    INSTANT_QUEUE = Field('instant_events')
    RABBIT_USER = Field('consumer')
    RABBIT_PASS = Field('qweqwe')
    RABBIT_HOST = Field('localhost')

    class Config:
        env_file = '../.env'
        env_file_encoding = 'utf-8'


settings = Settings()
