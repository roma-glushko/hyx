from typing import TYPE_CHECKING, Any

from hyx.common.events import ListenerRegistry
from hyx.fallback.typing import ResultT

if TYPE_CHECKING:
    from hyx.fallback.manager import FallbackManager

_FALLBACK_LISTENERS: ListenerRegistry["FallbackListener"] = ListenerRegistry()


class FallbackListener:
    async def on_fallback(self, fallback: "FallbackManager", result: ResultT, *args: Any, **kwargs: Any) -> None:
        ...


def register_timeout_listener(listener: FallbackListener) -> None:
    """
    Register a listener that will listen to all fallback components in the system
    """
    global _FALLBACK_LISTENERS

    _FALLBACK_LISTENERS.register(listener)
