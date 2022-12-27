from typing import Union, Callable, Iterator

BackoffT = Iterator[float]
JitterT = Callable[[float], float]

AttemptsT = Union[None, int]
BackoffsT = Union[int, float, BackoffT]
JittersT = Union[None, JitterT]
