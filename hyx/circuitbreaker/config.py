import dataclasses

from hyx.circuitbreaker.typing import DelayT
from hyx.common.typing import ExceptionsT


@dataclasses.dataclass
class BreakerConfig:
    exceptions: ExceptionsT
    failure_threshold: int
    recovery_delay_secs: DelayT
    recovery_threshold: int
