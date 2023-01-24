import asyncio

import httpx

from hyx.retry import retry


@retry(on=httpx.NetworkError, attempts=4)
async def get_gh_events() -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.github.com/events")

        return response.json()


asyncio.run(get_gh_events())
