from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hyx.timeout.manager import TimeoutManager


class TimeoutListener:
    """
    Listen to events dispatched by timeout components
    """

    async def on_timeout(self, timeout: "TimeoutManager") -> None:
        """
        Dispatch on timing out
        """
