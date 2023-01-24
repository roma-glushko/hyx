from typing import Any

import pytest

from hyx.fallback import fallback
from hyx.fallback.typing import ResultT


async def test__fallback__decorator() -> None:
    async def handler(result: ResultT, *args: Any, **kwargs: Any) -> str:
        return "falling back"

    @fallback(handler, on=Exception)
    async def imokay(degree: str = "a", *, totally: bool = True) -> str:
        adverb: str = "totally " if totally else ""

        return f"{adverb}{degree}-okay"

    assert await imokay() == "totally a-okay"
    assert await imokay("b") == "totally b-okay"
    assert await imokay("b", totally=False) == "b-okay"


async def test__fallback__on_failure() -> None:
    async def handler(result: ResultT, *args, **kwargs) -> str:
        return "falling back"

    @fallback(handler, on=(RuntimeError,))
    async def imokay() -> str:
        raise RuntimeError("runtime is not okay")

    assert await imokay() == "falling back"


async def test__fallback__passing_unknown_exceptions() -> None:
    async def handler(result: ResultT, *args, **kwargs) -> str:
        return "falling back"

    @fallback(handler, on=(RuntimeError,))
    async def imokay() -> str:
        raise ValueError("you should pass the mood arg")

    with pytest.raises(ValueError):
        await imokay()


async def test__fallback__predicate_only() -> None:
    async def handler(result: ResultT, *args, **kwargs) -> str:
        return "falling back"

    async def predicate(result: str, *args, **kwargs) -> bool:
        return "bad" in result

    @fallback(handler, on=None, if_=predicate)
    async def mood() -> str:
        return "i'm fine"

    assert await mood() == "i'm fine"


async def test__fallback__predicate_only_and_unknown_exceptions() -> None:
    async def handler(result: ResultT, *args, **kwargs) -> str:
        return "falling back"

    async def predicate(result: str, *args, **kwargs) -> bool:
        return "bad" in result

    @fallback(handler, on=None, if_=predicate)
    async def mood() -> str:
        raise ValueError

    with pytest.raises(ValueError):
        await mood()


async def test__fallback__predicate() -> None:
    async def handler(result: ResultT, *args, **kwargs) -> str:
        return "i'm okay"

    async def predicate(result: str, *args, **kwargs) -> bool:
        return "bad" in result

    @fallback(handler, on=(RuntimeError,), if_=predicate)
    async def mood() -> str:
        return "pretty bad"

    assert await mood() == "i'm okay"
