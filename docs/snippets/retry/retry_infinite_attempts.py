import asyncio

import httpx

from hyx.retry import retry
from hyx.retry.backoffs import expo

# Don't do this


@retry(on=httpx.NetworkError, attempts=None, backoff=expo(min_delay_secs=10, max_delay_secs=60))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("skiddo"))
