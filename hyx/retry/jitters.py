import random


def full(wait_time: float) -> float:
    """
    Full Interval Jitter

    Draw a jitter value from [0, upper_bound] interval uniformly

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """

    return random.uniform(0, wait_time)


def equal(wait_time: float) -> float:
    """
    Equal Jitter

    Reference: https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/
    """
    half_wait_time = 0.5 * wait_time

    return half_wait_time + random.uniform(0, half_wait_time)
