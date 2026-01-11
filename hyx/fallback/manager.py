from typing import Any

from hyx.fallback.events import FallbackListener
from hyx.fallback.typing import FallbackT, PredicateT
from hyx.typing import ExceptionsT, FuncT


class FallbackManager:
    """
    Call fallback handler on exceptions or conditions
    """

    __slots__ = (
        "_handler",
        "_exceptions",
        "_predicate",
        "_name",
        "_event_dispatcher",
    )

    def __init__(
        self,
        handler: FallbackT,
        event_dispatcher: FallbackListener,
        exceptions: ExceptionsT | None = None,
        predicate: PredicateT | None = None,
        name: str | None = None,
    ) -> None:
        self._handler = handler
        self._exceptions = exceptions
        self._predicate = predicate
        self._name = name
        self._event_dispatcher = event_dispatcher

    @property
    def name(self) -> str | None:
        return self._name

    async def __call__(self, func: FuncT, *args: Any, **kwargs: Any) -> Any:
        try:
            result = await func(*args, **kwargs)

            if self._predicate and await self._predicate(result, *args, **kwargs):
                await self._event_dispatcher.on_fallback(self, result, *args, **kwargs)
                return await self._handler(result, *args, **kwargs)

            return result
        except Exception as e:
            if self._exceptions and isinstance(e, self._exceptions):
                await self._event_dispatcher.on_fallback(self, e, *args, **kwargs)
                return await self._handler(e, *args, **kwargs)

            raise e
