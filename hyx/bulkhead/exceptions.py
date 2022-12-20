from hyx.common.exceptions import HyxError


class BulkheadFull(HyxError):
    """
    Occurs when execution requests has exceeded allowed amount
    """
