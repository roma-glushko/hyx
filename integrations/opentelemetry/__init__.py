from typing import Generic, TypeVar

from hyx.retry import register_retry_listener
from opentelemetry.metrics import Meter, MeterProvider

from hyx.retry.manager import RetryManager
from integrations.opentelemetry.retry import RetryMetricListener

ComponentT = TypeVar("ComponentT")
ListenerT = TypeVar("ListenerT")


class Factory(Generic[ComponentT, ListenerT]):
    def __init__(self, listener_class: type[ListenerT], *args, **kwargs) -> None:
        self.listener_class = listener_class

        self.args = args
        self.kwargs = kwargs

    async def __call__(self, component: ComponentT) -> ListenerT:
        return self.listener_class(component, *self.args, **self.kwargs)


class HyxOtelInstrumentor:
    def instrument(
        self,
        namespace: str = "hyx.service",
        meter: Meter | None = None,
        meter_provider: MeterProvider | None = None,
    ) -> None:
        register_retry_listener(
            Factory[RetryManager, RetryMetricListener](
                RetryMetricListener,
                namespace=namespace,
                meter=meter,
                meter_provider=meter_provider,
            ),
        )
