from typing import Any, Callable, Coroutine, Tuple, Type, TypeVar, Union

FuncT = TypeVar("FuncT", bound=Callable[..., Coroutine[Any, Any, Any]])
ExceptionsT = Union[Type[Exception], Tuple[Type[Exception], ...]]
