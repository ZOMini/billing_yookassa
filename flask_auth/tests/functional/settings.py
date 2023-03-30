import os
import sys

from pydantic import BaseSettings, Field

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(f'{BASE_DIR}\\flask_auth')


class TestSettings(BaseSettings):
    redis_host_t: str = Field(..., env='REDIS_HOST')
    redis_port_t: str = Field(..., env='REDIS_PORT')
    redis_url: str = Field(..., env='REDIS_URL')
    service_url: str = Field(..., env='SERVICE_URL')

    class Config:
        # .env - docker-compose /
        # .env - должны быть запущены образы(ES,REDIS,FASTAPI)
        # - в терминале: pytest ./src_test из папки funcional
        env_file = f'{BASE_DIR}/tests/functional/.env'


test_settings = TestSettings()
