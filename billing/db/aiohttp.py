import asyncio

import aiohttp


async def get_aiohttp() -> aiohttp.ClientSession:
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=35, loop=asyncio.get_event_loop())) as client:
        yield client
