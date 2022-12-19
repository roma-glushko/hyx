import asyncio


async def wait(seconds: float) -> None:
    """
    Abstract way the actual waiting function
    """
    await asyncio.sleep(seconds)
