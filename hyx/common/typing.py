from typing import Any, Awaitable, Callable, Type, TypeVar, Union, Tuple

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
ExceptionsT = Union[Type[BaseException], Tuple[Type[BaseException], ...]]
