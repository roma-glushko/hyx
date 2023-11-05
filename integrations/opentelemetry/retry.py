from hyx.retry.counters import Counter
from hyx.retry.events import RetryListener
from hyx.retry.manager import RetryManager

from opentelemetry.metrics import get_meter

from integrations.opentelemetry.__version__ import __version__


class RetryMetricListener(RetryListener):
    def __init__(self, retry: RetryManager, namespace: str, meter=None, meter_provider=None) -> None:
        if meter is None:
            meter = get_meter(__name__, __version__, meter_provider)

        self._meter = meter

        self._total_retries = meter.create_counter(name=f"{namespace}.{retry.name}.retries.count", unit="retries")
        self._total_failures = meter.create_counter(name=f"{namespace}.{retry.name}.retries.failures")
        self._success_after_retries = meter.create_histogram(name=f"{namespace}.{retry.name}.retries.success_after")

    async def on_retry(self, retry: "RetryManager", exception: Exception, counter: "Counter", backoff: float) -> None:
        self._total_retries.add(1)

    async def on_attempts_exceeded(self, retry: "RetryManager") -> None:
        self._total_failures.add(1)

    async def on_success(self, retry: "RetryManager", counter: "Counter"):
        self._success_after_retries.record(counter.current_attempt)
