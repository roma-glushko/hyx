import asyncio
import random
from functools import partial

import httpx

from hyx.retry import retry
from hyx.retry.backoffs import expo


def randomixin(delay: float, *, max_mixing: float = 20) -> float:
    """
    Custom Random Mixin Jitter
    """

    return delay + random.uniform(0, max_mixing)


@retry(on=httpx.NetworkError, backoff=expo(min_delay_secs=20, jitter=partial(randomixin, max_mixing=50)))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("cryogonal"))
