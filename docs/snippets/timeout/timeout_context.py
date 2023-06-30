import asyncio

from hyx.timeout import timeout


async def copy_directory(source_dir: str, destination_dir: str) -> None:
    """
    Copy a huge directory
    """
    async with timeout(1):
        ...


asyncio.run(copy_directory(source_dir="~/datasets", destination_dir="~/data"))
