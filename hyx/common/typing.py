from typing import Any, Awaitable, Callable, Type, TypeVar, Union

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
ExceptionsT = Union[Type[BaseException], tuple[Type[BaseException], ...]]
