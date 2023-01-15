from typing import Any, Awaitable, Callable, Tuple, Type, TypeVar, Union

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
ExceptionsT = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
