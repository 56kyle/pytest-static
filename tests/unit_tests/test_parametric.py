from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Literal
from typing import TypeVar

import pytest
from typing_extensions import ParamSpec
from typing_extensions import Protocol

from pytest_static.parametric import _iter_bool_instances
from pytest_static.parametric import _iter_bytes_instances
from pytest_static.parametric import _iter_callable_instances
from pytest_static.parametric import _iter_combinations
from pytest_static.parametric import _iter_complex_instances
from pytest_static.parametric import _iter_float_instances
from pytest_static.parametric import _iter_instances_using_fallback
from pytest_static.parametric import _iter_int_instances
from pytest_static.parametric import _iter_literal_instances
from pytest_static.parametric import _iter_none_instances
from pytest_static.parametric import _iter_protocol_instances
from pytest_static.parametric import _iter_str_instances
from pytest_static.parametric import _iter_type_var_instances
from pytest_static.parametric import get_all_possible_type_instances
from pytest_static.parametric import iter_instances
from pytest_static.parametric import type_handlers
from pytest_static.type_sets import DEFAULT_INSTANCE_SETS
from pytest_static.type_sets import INT_PARAMS
from tests.util import ANY_LEN
from tests.util import BASIC_TYPE_EXPECTED_EXAMPLES
from tests.util import BOOL_LEN
from tests.util import BYTES_LEN
from tests.util import COMPLEX_LEN
from tests.util import DUMMY_TYPE_HANDLER_OUTPUT
from tests.util import FLOAT_LEN
from tests.util import INT_LEN
from tests.util import NONE_LEN
from tests.util import PRODUCT_TYPE_EXPECTED_EXAMPLES
from tests.util import PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES
from tests.util import SPECIAL_TYPE_EXPECTED_EXAMPLES
from tests.util import STR_LEN
from tests.util import SUM_TYPE_EXPECTED_EXAMPLES
from tests.util import DummyProtocol
from tests.util import dummy_type_handler


if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable

    from _pytest.monkeypatch import MonkeyPatch

    from pytest_static.custom_typing import TypeHandler


NoneType: type[None] = type(None)


T = TypeVar("T", bound=Any)
P = ParamSpec("P")


T_temp_constrained = TypeVar("T_temp_constrained", int, str)
T_temp_bound = TypeVar("T_temp_bound", bound=int)
T_temp_any = TypeVar("T_temp_any")


class DummyClassNoArgs:
    pass


def dummy_callable(typ: Any) -> str:
    return str(typ)


def assert_len(iterable: Iterable[Any], expected: int) -> None:
    assert len([*iterable]) == expected


def test_module_level_registrations() -> None:
    from pytest_static.parametric import type_handlers as test_type_handlers

    assert len(test_type_handlers._mapping) > len(BASIC_TYPE_EXPECTED_EXAMPLES)


def test_get_all_possible_type_instances(monkeypatch: MonkeyPatch) -> None:
    def example_ints(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any]:
        yield from [1, 2, 3]

    monkeypatch.setitem(type_handlers._mapping, int, [example_ints])

    assert get_all_possible_type_instances(int) == (1, 2, 3)


@pytest.mark.parametrize(
    argnames=("typ", "expected_len"),
    argvalues=SPECIAL_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_special_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=("typ", "expected_len"),
    argvalues=BASIC_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=("typ", "expected_len"),
    argvalues=SUM_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_basic_sum_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=("typ", "expected_len"),
    argvalues=PRODUCT_TYPE_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_product_type(typ: Any, expected_len: int) -> None:
    assert_len(iter_instances(typ), expected_len)


@pytest.mark.parametrize(
    argnames=("typ", "expected_len"),
    argvalues=PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES,
    ids=lambda typ: f"{typ}",
)
def test_iter_instances_with_missing_generic_type(typ: Any, expected_len: int) -> None:
    assert expected_len == -1
    with pytest.raises(TypeError):
        assert [*iter_instances(typ)]


@pytest.mark.parametrize(argnames="key", argvalues=DEFAULT_INSTANCE_SETS.keys())
def test_type_handlers(key: Any) -> None:
    from pytest_static.parametric import type_handlers as test_handlers

    assert key in test_handlers._proxy


@pytest.mark.parametrize(
    argnames=("typ", "patched_function"),
    argvalues=[
        (T, _iter_type_var_instances),
        (dummy_type_handler, _iter_callable_instances),
        (DummyProtocol, _iter_protocol_instances),
    ],
)
def test__iter_instances_using_fallback(monkeypatch: MonkeyPatch, typ: Any, patched_function: TypeHandler) -> None:
    monkeypatch.setattr(f"pytest_static.parametric.{patched_function.__name__}", dummy_type_handler)
    assert_len(_iter_instances_using_fallback(typ, tuple()), len(DUMMY_TYPE_HANDLER_OUTPUT))


def test__iter_instances_using_fallback_with_invalid() -> None:
    with pytest.raises(TypeError):
        assert [*_iter_instances_using_fallback(42, tuple())]


@pytest.mark.parametrize(
    argnames=("base_type", "type_args", "expected_len"),
    argvalues=[
        (T_temp_constrained, tuple(), INT_LEN + STR_LEN),
        (T_temp_bound, tuple(), INT_LEN),
        (T_temp_any, tuple(), ANY_LEN),
    ],
)
def test__iter_type_var_instances(base_type: Any, type_args: tuple[Any, ...], expected_len: int) -> None:
    assert_len(_iter_type_var_instances(base_type, type_args), expected_len)


def test__iter_protocol_instances() -> None:
    class DummyProtocolB(Protocol):
        def dummy_method(self, x: int) -> None: ...  # pragma: no cover

    with pytest.raises(NotImplementedError):
        _iter_protocol_instances(DummyProtocolB, tuple())


def test__iter_callable_instances() -> None:
    assert_len(_iter_callable_instances(dummy_callable, tuple()), ANY_LEN)


@pytest.mark.parametrize(
    argnames=("type_args", "expected_len"),
    argvalues=[
        ((int,), INT_LEN),
        ((int, str), INT_LEN * STR_LEN),
        ((int, str, float), INT_LEN * STR_LEN * FLOAT_LEN),
    ],
)
def test__iter_combinations(type_args: tuple[Any, ...], expected_len: int) -> None:
    combinations: list[tuple[Any, ...]] = list(_iter_combinations(type_args))
    assert_len(combinations, expected_len)


def test__iter_none_instances() -> None:
    assert_len(_iter_none_instances(None, ()), NONE_LEN)


def test__iter_bool_instances() -> None:
    assert_len(_iter_bool_instances(bool, ()), BOOL_LEN)


def test__iter_int_instances() -> None:
    assert_len(_iter_int_instances(int, ()), INT_LEN)


def test__iter_float_instances() -> None:
    assert_len(_iter_float_instances(float, ()), FLOAT_LEN)


def test__iter_complex_instances() -> None:
    assert_len(_iter_complex_instances(complex, ()), COMPLEX_LEN)


def test__iter_str_instances() -> None:
    assert_len(_iter_str_instances(str, ()), STR_LEN)


def test__iter_bytes_instances() -> None:
    assert_len(_iter_bytes_instances(bytes, ()), BYTES_LEN)


def test__iter_literal_instances() -> None:
    assert_len(_iter_literal_instances(Literal, tuple(INT_PARAMS)), INT_LEN)
