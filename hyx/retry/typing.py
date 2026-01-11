from collections.abc import Callable, Iterator, Sequence

BackoffT = Iterator[float]
JitterT = Callable[[float], float]

AttemptsT = None | int
BackoffsT = int | float | Sequence[float] | BackoffT
JittersT = None | JitterT

BucketRetryT = None | int
