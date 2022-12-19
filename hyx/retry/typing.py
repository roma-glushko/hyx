from typing import Any, AsyncGenerator, AsyncIterator, Awaitable, Callable, Sequence, Type, TypeVar, Union

BackoffT = AsyncIterator[float]
JitterT = AsyncGenerator[float, None]

RetryOnT = Union[Type[BaseException], Sequence[Type[BaseException]]]
AttemptsT = Union[None, int]
BackoffsT = Union[int, float, BackoffT]
JittersT = Union[None, JitterT]
RetryableFuncT = TypeVar("RetryableFuncT", bound=Callable[..., Awaitable[Any]])
