from typing import AsyncGenerator, AsyncIterator, Union

BackoffT = AsyncIterator[float]
JitterT = AsyncGenerator[float, None]

AttemptsT = Union[None, int]
BackoffsT = Union[int, float, BackoffT]
JittersT = Union[None, JitterT]
