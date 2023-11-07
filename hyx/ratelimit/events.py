from typing import TYPE_CHECKING, Union

from hyx.events import ListenerFactoryT, ListenerRegistry

if TYPE_CHECKING:
    from hyx.ratelimit.managers import RateLimiter

_RATELIMITER_LISTENERS: ListenerRegistry["RateLimiter", "RateLimiterListener"] = ListenerRegistry()


class RateLimiterListener:
    ...


def register_ratelimiter_listener(listener: Union[RateLimiterListener, ListenerFactoryT]) -> None:
    """
    Register a listener that will listen to all rate limiter components in the system
    """
    global _RATELIMITER_LISTENERS

    _RATELIMITER_LISTENERS.register(listener)
