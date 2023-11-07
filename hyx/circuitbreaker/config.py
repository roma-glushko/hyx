import dataclasses

from hyx.circuitbreaker.typing import DelayT
from hyx.typing import ExceptionsT


@dataclasses.dataclass
class BreakerConfig:
    exceptions: ExceptionsT
    failure_threshold: int
    recovery_time_secs: DelayT
    recovery_threshold: int
