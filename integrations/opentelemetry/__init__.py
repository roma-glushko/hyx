from hyx.retry import register_retry_listener
from integrations.opentelemetry.retry import RetryMetricListener


class OtelMetricInstrumentor:
    def instrument(self, namespace: str = "hyx") -> None:
        register_retry_listener(RetryMetricListener)
