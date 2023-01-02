import asyncio

import httpx

from hyx.retry import retry


@retry(on=httpx.NetworkError, attempts=4, backoff=(0.5, 1.0, 1.5, 2.0))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("slowpoke"))
