from typing import Callable, Iterator, Sequence, Union

BackoffT = Iterator[float]
JitterT = Callable[[float], float]

AttemptsT = Union[None, int]
BackoffsT = Union[int, float, Sequence[float], BackoffT]
JittersT = Union[None, JitterT]

BucketRetryT = Union[None, int]
