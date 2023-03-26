from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    api_requests_count = 100
    yoo_post_url: str = Field('https://localhost/yookassa/api/v1/buy_subscription/ffe0d805-3595-4cc2-a892-f2bedbec4ac6')

    class Config:
        env_file = '../.env'


settings = Settings()
