from hyx.retry import retry


async def test__retry__decorate_async_func() -> None:
    @retry()
    async def simple_func() -> int:
        return 2022

    await simple_func()
