import asyncio

from hyx.timeout import timeout


@timeout(max_delay_secs=1)
async def copy_directory(source_dir: str, destination_dir: str) -> None:
    """
    Copy a huge directory
    """
    ...

asyncio.run(copy_directory(source_dir="~/datasets", destination_dir="~/data"))
