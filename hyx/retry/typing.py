from typing import Callable, Iterator, Union

BackoffT = Iterator[float]
JitterT = Callable[[float], float]

AttemptsT = Union[None, int]
BackoffsT = Union[int, float, BackoffT]
JittersT = Union[None, JitterT]
