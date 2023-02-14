import asyncio
from typing import Any

from hyx.fallback import fallback
from hyx.fallback.typing import ResultT


def get_default_user_avatar(result: ResultT, *args: Any, **kwargs: Any) -> Any:
    """
    If `get_user_avatar()` fails, this function will return a default placeholder
    """
    ...


@fallback(get_default_user_avatar, on=ConnectionError)
async def get_user_avatar(user_id: str) -> bytes:
    """
    Get user avatar from the object storage
    """
    ...


asyncio.run(get_user_avatar(user_id="1234"))
