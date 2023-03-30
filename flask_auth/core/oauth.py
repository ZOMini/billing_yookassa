from authlib.integrations.flask_client import OAuth

from core.config import settings
from db.redis import jwt_redis_blocklist


def init_oauth(app):
    oauth = OAuth(app, cache=jwt_redis_blocklist)
    oauth.register(
        'yandex',
        response_type='code',
        client_id=settings.YANDEX_CLIENT_ID,
        client_secret=settings.YANDEX_CLIENT_SECRET,
        api_base_url=settings.YANDEX_API_BASE_URL,
        access_token_url=settings.YANDEX_ACCESS_TOKEN_URL,
        authorize_url=settings.YANDEX_AUTHORIZE_URL,
        # force_confirm='yes'
        # scope=['openid','profile','email'],
        # client_kwargs={'scope': 'openid profile email'},
    )
    oauth.register(
        'vk',
        response_type='code',
        client_id=settings.VK_CLIENT_ID,
        client_secret=settings.VK_CLIENT_SECRET,
        api_base_url=settings.VK_API_BASE_URL,
        access_token_url=settings.VK_ACCESS_TOKEN_URL,
        authorize_url=settings.VK_AUTHORIZE_URL,
        client_kwargs={"token_placement": "uri", "token_endpoint_auth_method": "client_secret_post", "scope": "email"}
    )

    oauth.register(
        'google',
        response_type='code',
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        api_base_url=settings.GOOGLE_API_BASE_URL,
        access_token_url=settings.GOOGLE_ACCESS_TOKEN_URL,
        authorize_url=settings.GOOGLE_AUTHORIZE_URL,
        client_kwargs={"scope": "openid profile email"}
    )
