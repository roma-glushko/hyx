from typing import TypeVar, Callable, Awaitable, Any, Union

DurationT = Union[int, float]
FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
