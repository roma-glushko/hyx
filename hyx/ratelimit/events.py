from typing import TYPE_CHECKING

from hyx.events import ListenerFactoryT, ListenerRegistry

if TYPE_CHECKING:
    from hyx.ratelimit.managers import RateLimiter

_RATELIMITER_LISTENERS: ListenerRegistry["RateLimiter", "RateLimiterListener"] = ListenerRegistry()


class RateLimiterListener:
    """
    Listen to events dispatched by rate limiter components.
    """

    async def on_rate_limited(self, limiter: "RateLimiter") -> None:
        """
        Dispatch when a request is rejected due to rate limiting.
        """


def register_ratelimiter_listener(listener: RateLimiterListener | ListenerFactoryT) -> None:
    """
    Register a listener that will listen to all rate limiter components in the system.
    """
    global _RATELIMITER_LISTENERS

    _RATELIMITER_LISTENERS.register(listener)
