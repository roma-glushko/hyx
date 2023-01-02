import asyncio

import httpx

from hyx.retry import retry


@retry(on=httpx.NetworkError, backoff=0.5)  # delay 500ms on each retry
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("pikachu"))
