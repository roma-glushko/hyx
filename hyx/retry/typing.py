from typing import Any, AsyncGenerator, AsyncIterator, Awaitable, Callable, Sequence, TypeVar, Union, Type

BackoffT = AsyncIterator[float]
JitterT = AsyncGenerator[float, None]

RetryOnT = Union[Type[Exception], Sequence[Type[Exception]]]
AttemptsT = Union[None, int]
BackoffsT = Union[int, float, BackoffT]
JitterT = Union[None, JitterT]
RetryableFuncT = TypeVar("RetryableFuncT", bound=Callable[..., Awaitable[Any]])
