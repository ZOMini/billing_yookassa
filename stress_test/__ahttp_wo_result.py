import asyncio
import logging
import time

import aiohttp
import orjson

from config import settings


def orjson_dumps(v):
    return orjson.dumps(v).decode()


loop = asyncio.new_event_loop()
conn = aiohttp.TCPConnector(limit=0, loop=loop)


async def q1():
    async with aiohttp.ClientSession(connector=conn, json_serialize=orjson_dumps) as session:
        for i in range(settings.API_REQUESTS_COUNT):
            await session.post(settings.API_KAFKA_POST, json={"topic": "rating", "user_id": "500271", "movie_id": "tt0120338", "value": i})
start_time = time.time()
loop.run_until_complete(q1())
# asyncio.run(q1())
logging.error('INFO - All ok: time - %s seconds', (time.time() - start_time))
