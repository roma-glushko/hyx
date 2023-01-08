import asyncio
from typing import Any

import httpx

from hyx.circuitbreaker import consecutive_breaker


class InventoryTemporaryError(RuntimeError):
    """
    Occurs when the inventory microservice is temporary inaccessible
    """


breaker = consecutive_breaker(exceptions=(InventoryTemporaryError,), failure_threshold=5, recovery_delay_secs=30)


@breaker
async def get_product_qty_left(product_sku: str) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://inventory.shop/{product_sku}/")

        if response.status_code >= 500:
            raise InventoryTemporaryError

        return response.json()


asyncio.run(get_product_qty_left("guido-van-rossum-portrait"))
