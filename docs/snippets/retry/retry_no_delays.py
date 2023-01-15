import asyncio

import httpx

from hyx.retry import retry

# Don't do this


@retry(on=httpx.NetworkError, backoff=0.0)
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("noibat"))
