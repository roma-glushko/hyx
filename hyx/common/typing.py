from typing import Any, Awaitable, Callable, Sequence, Type, TypeVar, Union

FuncT = TypeVar("FuncT", bound=Callable[..., Awaitable[Any]])
ExceptionsT = Union[Type[BaseException], Sequence[Type[BaseException]]]
