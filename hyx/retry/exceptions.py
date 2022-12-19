from hyx.common.exceptions import HyxError


class MaxAttemptsExceeded(HyxError):
    """
    Occurs when all attempts were exceeded with no success
    """
