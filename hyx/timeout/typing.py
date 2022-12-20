from typing import Any, Awaitable, Callable, TypeVar, Union

DurationT = Union[int, float]
FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
