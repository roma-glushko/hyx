from hyx.exceptions import HyxError


class AttemptsExceeded(HyxError):
    """
    Occurs when all attempts were exceeded with no success
    """
