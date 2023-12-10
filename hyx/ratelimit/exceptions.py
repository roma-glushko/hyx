from hyx.exceptions import HyxError


class RateLimitExceeded(HyxError):
    """
    Occurs when requester has exceeded the rate limit
    """


class EmptyBucket(HyxError):
    """
    Occurs when requester has exceeded the rate limit and the bucket is empty
    Exception is thrown in the token bucket rate limiter
    """


class FilledBucket(HyxError):
    """
    Occurs when requester has exceeded the rate limit and the bucket is full
    Exception is thrown in the leaky bucket rate limiter
    """
