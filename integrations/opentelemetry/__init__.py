from typing import Optional, Generic, Type, TypeVar

from hyx.retry import register_retry_listener
from opentelemetry.metrics import Meter, MeterProvider

from hyx.retry.manager import RetryManager
from integrations.opentelemetry.retry import RetryMetricListener

ComponentT = TypeVar("ComponentT")
ListenerT = TypeVar("ListenerT")


class Factory(Generic[ComponentT, ListenerT]):
    def __init__(self, listener_class: Type[ListenerT], *args, **kwargs) -> None:
        self.listener_class = listener_class

        self.args = args
        self.kwargs = kwargs

    async def __call__(self, component: ComponentT) -> ListenerT:
        return self.listener_class(component, *self.args, **self.kwargs)


class HyxOtelInstrumentor:
    def instrument(
        self,
        namespace: str = "hyx.service",
        meter: Optional[Meter] = None,
        meter_provider: Optional[MeterProvider] = None,
    ) -> None:
        register_retry_listener(
            Factory[RetryManager, RetryMetricListener](
                RetryMetricListener,
                namespace=namespace,
                meter=meter,
                meter_provider=meter_provider,
            ),
        )
