import asyncio

import httpx

from hyx.retry import retry
from hyx.retry.backoffs import fibo


@retry(on=httpx.NetworkError, backoff=fibo(min_delay_secs=10, factor_secs=5))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("kartana"))
