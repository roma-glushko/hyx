from hyx.common.exceptions import HyxError


class MaxDurationExceeded(HyxError):
    """
    Occurs if some task took more time then it was given
    """