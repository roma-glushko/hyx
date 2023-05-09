import dataclasses

from hyx.circuitbreaker import BreakerListener
from hyx.circuitbreaker.typing import DelayT
from hyx.common.typing import ExceptionsT


@dataclasses.dataclass
class BreakerConfig:
    exceptions: ExceptionsT
    failure_threshold: int
    recovery_time_secs: DelayT
    recovery_threshold: int
    event_dispatcher: BreakerListener
