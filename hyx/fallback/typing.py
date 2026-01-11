from typing import Any, Protocol

ResultT = BaseException | Any


class PredicateT(Protocol):
    async def __call__(self, result: Any, *args, **kwargs) -> bool: ...


class FallbackT(Protocol):
    async def __call__(self, result: ResultT, *args: Any, **kwargs: Any) -> Any: ...
