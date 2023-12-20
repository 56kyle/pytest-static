from __future__ import annotations

from typing import Any
from typing import Generator
from typing import ParamSpec
from typing import TypeVar

from _pytest.monkeypatch import MonkeyPatch

import pytest_static
from pytest_static.parametric import get_all_possible_type_instances


NoneType: type[None] = type(None)


T = TypeVar("T", bound=Any)
P = ParamSpec("P")


class DummyClassNoArgs:
    pass


def dummy_iter_instances(typ: Any) -> Generator[Any, None, None]:
    yield from (1, 2, 3)


def test_get_all_possible_type_instances(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        pytest_static.parametric, "iter_instances", dummy_iter_instances
    )
    assert get_all_possible_type_instances(str) == (1, 2, 3)
