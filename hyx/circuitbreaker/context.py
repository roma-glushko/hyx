import dataclasses
from typing import TYPE_CHECKING, Optional

from hyx.circuitbreaker.typing import DelayT
from hyx.typing import ExceptionsT

if TYPE_CHECKING:
    from hyx.circuitbreaker import BreakerListener


@dataclasses.dataclass
class BreakerContext:
    breaker_name: Optional[str]
    exceptions: ExceptionsT
    failure_threshold: int
    recovery_time_secs: DelayT
    recovery_threshold: int
    event_dispatcher: "BreakerListener"
