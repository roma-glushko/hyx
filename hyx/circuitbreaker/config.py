import dataclasses
from typing import TYPE_CHECKING

from hyx.circuitbreaker.typing import DelayT
from hyx.common.typing import ExceptionsT

if TYPE_CHECKING:
    from hyx.circuitbreaker import BreakerListener


@dataclasses.dataclass
class BreakerConfig:
    breaker_name: str
    exceptions: ExceptionsT
    failure_threshold: int
    recovery_time_secs: DelayT
    recovery_threshold: int
    event_dispatcher: "BreakerListener"
