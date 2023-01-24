import asyncio

import httpx

from hyx.retry import jitters, retry
from hyx.retry.backoffs import expo


@retry(on=httpx.NetworkError, backoff=expo(min_delay_secs=10, max_delay_secs=60, jitter=jitters.full))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("psyduck"))
