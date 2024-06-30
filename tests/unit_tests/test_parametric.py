from __future__ import annotations

from typing import Any
from typing import Generator
from typing import Iterable
from typing import TypeVar

import pytest
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import ParamSpec

from pytest_static.parametric import get_all_possible_type_instances
from pytest_static.parametric import type_handlers
from tests.util import BASIC_TYPE_EXPECTED_EXAMPLES
from tests.util import PRODUCT_TYPE_EXPECTED_EXAMPLES
from tests.util import PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES
from tests.util import SPECIAL_TYPE_EXPECTED_EXAMPLES
from tests.util import SUM_TYPE_EXPECTED_EXAMPLES


NoneType: type[None] = type(None)


T = TypeVar("T", bound=Any)
P = ParamSpec("P")


class DummyClassNoArgs:
    pass


def dummy_iter_instances(typ: Any) -> Generator[Any, None, None]:
    yield from (1, 2, 3)


def assert_len(iterable: Iterable[Any], expected: int) -> None:
    assert len([*iterable]) == expected


def test_get_all_possible_type_instances(monkeypatch: MonkeyPatch) -> None:
    def example_ints(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
        yield from [1, 2, 3]

    monkeypatch.setitem(type_handlers._mapping, int, [example_ints])

    assert get_all_possible_type_instances(int) == (1, 2, 3)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=SPECIAL_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_special_type(typ: Any, expected_len: int) -> None:
    assert_len(type_handlers.iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=BASIC_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_type(typ: Any, expected_len: int) -> None:
    assert_len(type_handlers.iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=SUM_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_sum_type(typ: Any, expected_len: int) -> None:
    assert_len(type_handlers.iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=PRODUCT_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_product_type(typ: Any, expected_len: int) -> None:
    assert_len(type_handlers.iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_missing_generic_type(typ: Any, expected_len: int) -> None:
    assert expected_len == -1
    with pytest.raises(TypeError):
        assert [*type_handlers.iter_instances(typ)]
