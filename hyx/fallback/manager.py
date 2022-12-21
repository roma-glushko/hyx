from typing import Any, Optional

from hyx.common.typing import ExceptionsT, FuncT
from hyx.fallback.typing import FallbackT, PredicateT


class FallbackManager:
    """
    Call fallback handler on exceptions or conditions
    """
    def __init__(
        self,
        handler: FallbackT,
        exceptions: Optional[ExceptionsT] = None,
        predicate: Optional[PredicateT] = None,
    ) -> None:
        self._handler = handler
        self._exceptions = exceptions
        self._predicate = predicate

    async def __call__(self, func: FuncT, *args: Any, **kwargs: Any) -> Any:
        try:
            result = await func(*args, **kwargs)

            if self._predicate and await self._predicate(result, *args, **kwargs):
                return await self._handler(result, *args, **kwargs)

            return result
        except Exception as e:
            if self._exceptions and isinstance(e, self._exceptions):
                return await self._handler(e, *args, **kwargs)

            raise e
