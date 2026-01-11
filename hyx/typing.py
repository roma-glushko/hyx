from typing import Any, Callable, Coroutine, TypeVar

FuncT = TypeVar("FuncT", bound=Callable[..., Coroutine[Any, Any, Any]])
ExceptionsT = type[Exception] | tuple[type[Exception], ...]
