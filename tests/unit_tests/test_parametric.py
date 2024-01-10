from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from typing import Generator
from typing import Iterable
from typing import ParamSpec
from typing import TypeVar

import pytest
from _pytest.monkeypatch import MonkeyPatch

import pytest_static
from pytest_static.parametric import get_all_possible_type_instances
from pytest_static.parametric import iter_instances
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
    monkeypatch.setattr(
        pytest_static.parametric, "iter_instances", dummy_iter_instances
    )
    assert get_all_possible_type_instances(int) == (1, 2, 3)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=SPECIAL_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_special_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=BASIC_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=SUM_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_sum_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=PRODUCT_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_product_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=["typ", "expected_len"],
    argvalues=PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_missing_generic_type(typ: Any, expected_len: int) -> None:
    assert expected_len == -1
    with pytest.raises(TypeError):
        assert [*iter_instances(typ)]


def test_iter_instances_with_custom_type() -> None:
    @dataclass
    class CustomType:
        x: int
        y: str

    with pytest.raises(NotImplementedError):
        _: list[Any] = [*iter_instances(CustomType)]
