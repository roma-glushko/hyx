import asyncio
from typing import Iterator

import httpx

from hyx.retry import retry
from hyx.retry.backoffs import MS_TO_SECS, SECS_TO_MS


class factorial(Iterator[float]):
    """
    Custom Factorial Backoff
    """

    def __init__(
        self,
        *,
        min_delay_secs: float = 1,
    ) -> None:
        self._min_delay_ms = min_delay_secs * SECS_TO_MS

        self._current_delay_ms = self._min_delay_ms

    def __iter__(self) -> "factorial":
        self._current_delay_ms = self._min_delay_ms

        return self

    def __next__(self) -> float:
        current_delay_ms = self._current_delay_ms

        self._current_delay_ms *= self._current_delay_ms + 1

        return current_delay_ms * MS_TO_SECS


@retry(on=httpx.NetworkError, backoff=factorial(min_delay_secs=20))
async def get_poke_data(pokemon: str) -> None:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://pokeapi.co/api/v2/pokemon/{pokemon}")

        return response.json()


asyncio.run(get_poke_data("fomantis"))
