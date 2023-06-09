import asyncio
import logging
import time
from collections import defaultdict

import aiohttp
import orjson
from config import settings


async def ahttp_test(i: int):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop(), verify_ssl=False)) as client:
        return await client.get(settings.yoo_post_url)


async def main():
    start_time = time.time()
    tasks = [asyncio.ensure_future(
             ahttp_test(i)) for i in range(settings.api_requests_count)]
    done, _ = await asyncio.wait(tasks)
    result = defaultdict(int)
    for future in done:
        result[future.result().status] += 1
    logging.error('INFO - All ok: time - %s seconds, ok - %s, error - %s', (time.time() - start_time), result[200], settings.api_requests_count - result[200])

loop = asyncio.new_event_loop()
loop.run_until_complete(main())
loop.close()
