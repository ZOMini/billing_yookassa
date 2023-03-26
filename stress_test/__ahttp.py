import asyncio
import logging
import time

import aiohttp
import orjson

from config import settings


async def ahttp_test(i: int):
    async with aiohttp.ClientSession() as client:
        headers = {'CONTENT-TYPE': 'application/json'}
        _json = orjson.dumps({"topic": "rating", "user_id": "500271", "movie_id": "tt0120338", "value": i})
        await client.post(settings.API_KAFKA_POST, data=_json, headers=headers)


async def main():
    start_time = time.time()
    tasks = [asyncio.ensure_future(
             ahttp_test(i)) for i in range(settings.API_REQUESTS_COUNT)]
    await asyncio.wait(tasks)
    logging.error('INFO - All ok: time - %s seconds', (time.time() - start_time))

asyncio.run(main())
