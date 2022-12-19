import random
from typing import AsyncGenerator


async def full(upper_bound: float) -> AsyncGenerator[float, None]:
    """
    Full Interval Jitter

    Draw a jitter value from [0, upper_bound] interval uniformly

    Reference: http://www.awsarchitectureblog.com/2015/03/backoff.html
    """

    yield random.uniform(0, upper_bound)


async def rand(fixed_part: float) -> AsyncGenerator[float, None]:
    """
    Fixed value with some random number of milliseconds
    """
    yield fixed_part + random.random()
