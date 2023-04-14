import aioredis
import uvicorn
import var_dump as var_dump
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse

from api.v1 import yookassa
from core.config import settings
from db import redis
from db.pg import async_session, init_db
from models.models_pg import test_data

app = FastAPI(
    title='Billing',
    docs_url='/yookassa/api/openapi',
    openapi_url='/yookassa/api/openapi.json',
    default_response_class=ORJSONResponse,
)

app.include_router(yookassa.router, prefix='/yookassa/api/v1', tags=['yookassa'])


@app.on_event('startup')
async def startup():
    await init_db()
    await test_data()
    redis.redis = await aioredis.from_url(
        f'redis://{settings.redis_bill}:{settings.redis_port}',
        decode_responses=True, max_connections=128)


@app.on_event('shutdown')
async def shutdown():
    redis.redis.close()
    await redis.redis.close()
    async_session.close_all()

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=443, limit_max_requests=128, workers=1, reload=True)
