import functools
from typing import Any, Callable, Optional, Sequence, cast

from hyx.events import EventDispatcher, EventManager, get_default_name
from hyx.fallback.events import _FALLBACK_LISTENERS, FallbackListener
from hyx.fallback.manager import FallbackManager
from hyx.fallback.typing import FallbackT, PredicateT
from hyx.typing import ExceptionsT, FuncT


def fallback(
    handler: FallbackT,
    *,
    name: Optional[str] = None,
    on: Optional[ExceptionsT] = Exception,
    if_: Optional[PredicateT] = None,
    listeners: Optional[Sequence[FallbackListener]] = None,
    event_manager: Optional["EventManager"] = None,
) -> Callable[[Callable], Callable]:
    """
    Provides a fallback on exceptions and/or specific result of the original function

    **Parameters**

    * **handler** *(Callable)* - The fallback handler
    * **on** *(None | Exception | tuple[Exception, ...])* - Fall back on the give exception(s)
    * **if_** *(None | Callable)* - Fall back if the given predicate function returns True
        on the original function result
    * **name** *(None | str)* - A component name or ID (will be passed to listeners and mention in metrics)
    * **listeners** *(None | Sequence[TimeoutListener])* - List of listeners of this concreate component state
    """
    if not on and not if_:
        raise ValueError("Either on or if_ param should be specified when using the fallback decorator")

    def _decorator(func: FuncT) -> FuncT:
        event_dispatcher = EventDispatcher[FallbackManager, FallbackListener](
            listeners,
            _FALLBACK_LISTENERS,
            event_manager=event_manager,
        )

        manager = FallbackManager(
            name=name or get_default_name(func),
            handler=handler,
            exceptions=on,
            predicate=if_,
            event_dispatcher=event_dispatcher.as_listener,
        )

        event_dispatcher.set_component(manager)

        @functools.wraps(func)
        async def _wrapper(*args: Any, **kwargs: Any) -> Any:
            return await manager(func, *args, **kwargs)

        _wrapper._original = func  # type: ignore[attr-defined]
        _wrapper._manager = manager  # type: ignore[attr-defined]

        return cast(FuncT, _wrapper)

    return _decorator
