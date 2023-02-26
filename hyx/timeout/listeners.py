from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hyx.timeout.manager import TimeoutManager


class TimeoutListener:
    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        ...
