from datetime import timedelta

from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    postgres_db: str = Field(...)
    postgres_user: str = Field(...)
    postgres_password: str = Field(...)
    postgres_host: str = Field(...)
    postgres_port: int = Field(...)

    redis_host: str = Field(...)
    redis_port: int = Field(...)
    redis_url: str = Field(...)
    redis_expire: int = Field(...)

    yoo_account_id: str = Field(...)
    yoo_secret_key: str = Field(...)

    jwt_super: str = Field(...)
    auth_role_url: str = 'http://flask_auth:5000/auth/api/v1/user/roles/billing'

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'

settings = Settings()
