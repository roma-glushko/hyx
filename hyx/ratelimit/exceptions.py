from hyx.exceptions import HyxError


class RateLimitExceeded(HyxError):
    """
    Occurs when requester have exceeded the rate limit
    """
