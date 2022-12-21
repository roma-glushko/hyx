from hyx.common.exceptions import HyxError


class BreakerFailing(HyxError):
    """
    Occurs when you try to execute actions that was identified as failing by the circuit breaker
    """
