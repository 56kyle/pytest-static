"""A Python module used for parameterizing Literal's and common types."""

from __future__ import annotations

import itertools
from enum import Enum
from functools import partial
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Optional
from typing import Sequence
from typing import Union
from typing import get_args

from _pytest.mark import Mark
from _pytest.python import Metafunc
from typing_extensions import Literal

from pytest_static.custom_typing import KT
from pytest_static.custom_typing import VT
from pytest_static.custom_typing import T
from pytest_static.custom_typing import T_co
from pytest_static.custom_typing import TypeHandler
from pytest_static.custom_typing import _ScopeName
from pytest_static.type_handler import TypeHandlerRegistry
from pytest_static.type_sets import BOOL_PARAMS
from pytest_static.type_sets import BYTES_PARAMS
from pytest_static.type_sets import COMPLEX_PARAMS
from pytest_static.type_sets import DEFAULT_INSTANCE_SETS
from pytest_static.type_sets import FLOAT_PARAMS
from pytest_static.type_sets import INT_PARAMS
from pytest_static.type_sets import STR_PARAMS
from pytest_static.util import get_base_type


type_handlers: TypeHandlerRegistry = TypeHandlerRegistry()


def parametrize_types(
    metafunc: Metafunc,
    argnames: str | Sequence[str],
    argtypes: list[type[T]],
    indirect: bool | Sequence[str] = False,
    ids: Iterable[object | None] | Callable[[Any], object | None] | None = None,
    scope: _ScopeName | None = None,
    *,
    _param_mark: Mark | None = None,
) -> None:
    """Pytest marker emulating pytest parametrize but using types to specify sets."""
    argnames = _ensure_sequence(argnames)
    if len(argnames) != len(argtypes):
        raise ValueError("Parameter names and types count must match.")

    parameter_sets: list[list[T]] = [list(get_all_possible_type_instances(t)) for t in argtypes]
    parameter_combinations: list[tuple[T, ...]] = list(itertools.product(*parameter_sets))

    if ids is None:
        ids = [", ".join(map(repr, pairs)) for pairs in parameter_combinations]

    metafunc.parametrize(
        argnames=argnames,
        argvalues=parameter_combinations,
        indirect=indirect,
        ids=ids,
        scope=scope,
        _param_mark=_param_mark,
    )


def _ensure_sequence(value: str | Sequence[str]) -> Sequence[str]:
    if isinstance(value, str):
        return value.split(", ")
    return value


def get_all_possible_type_instances(type_argument: Any) -> tuple[Any, ...]:
    """Gets all possible instances for the given type."""
    return tuple(iter_instances(type_argument))


def iter_instances(key: Any, handler_registry: TypeHandlerRegistry = type_handlers) -> Generator[Any, None, None]:
    """Returns a Generator that yields from all handlers."""
    base_type: Any = get_base_type(key)
    type_args: tuple[Any, ...] = get_args(key)

    handlers: Iterable[TypeHandler] | None = handler_registry.get(base_type, None)
    if handlers is None:
        raise KeyError(f"Failed to find a handler for {key=}.")
    for handler in handlers:
        yield from handler(base_type, type_args)


@type_handlers.register(type(None))
def _iter_none_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield None


@type_handlers.register(bool)
def _iter_bool_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from BOOL_PARAMS


@type_handlers.register(int)
def _iter_int_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from INT_PARAMS


@type_handlers.register(float)
def _iter_float_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from FLOAT_PARAMS


@type_handlers.register(complex)
def _iter_complex_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from COMPLEX_PARAMS


@type_handlers.register(str)
def _iter_str_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from STR_PARAMS


@type_handlers.register(bytes)
def _iter_bytes_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from BYTES_PARAMS


@type_handlers.register(Literal)
def _iter_literal_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from type_args


@type_handlers.register(Any)
def _iter_any_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    for typ in DEFAULT_INSTANCE_SETS.keys():
        yield from iter_instances(typ)


@type_handlers.register(Union, Optional, Enum)
def _iter_sum_instances(_: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    for arg in type_args:
        yield from get_all_possible_type_instances(arg)


def _iter_combinations(type_args: tuple[Any, ...]) -> Generator[tuple[Any, ...], None, None]:
    yield from map(tuple, itertools.product(*map(iter_instances, type_args)))


def _iter_product_instances_with_constructor(
    _: Any,
    type_args: tuple[Any, ...],
    /,
    type_constructor: Callable[[tuple[Any, ...]], T_co],
) -> Generator[T_co, None, None]:
    if Ellipsis in type_args:
        type_args = type_args[:-1]
    yield from map(type_constructor, _iter_combinations(type_args))


def _validate_combination_length(combination: tuple[Any, ...], expected_length: int, typ: type[Any]) -> None:
    if len(combination) != expected_length:
        raise TypeError(f"Expected combination of length {expected_length} for " f"type {typ}. Got {len(combination)}")


def _iter_custom_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    """Planned for future, but not yet implemented."""
    raise NotImplementedError


def _dict_constructor(combination: tuple[KT, VT]) -> dict[KT, VT]:
    _validate_combination_length(combination=combination, expected_length=2, typ=dict)
    return {combination[0]: combination[1]}


def _list_constructor(combination: tuple[T]) -> list[T]:
    _validate_combination_length(combination=combination, expected_length=1, typ=list)
    return list(combination)


def _set_constructor(combination: tuple[T]) -> set[T]:
    _validate_combination_length(combination=combination, expected_length=1, typ=set)
    return set(combination)


def _frozenset_constructor(combination: tuple[T]) -> frozenset[T]:
    _validate_combination_length(combination=combination, expected_length=1, typ=frozenset)
    return frozenset(combination)


def _tuple_constructor(combination: T) -> T:
    return combination


_iter_dict_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_dict_constructor
)
type_handlers.register(dict)(_iter_dict_instances)


_iter_list_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_list_constructor
)
type_handlers.register(list)(_iter_list_instances)


_iter_set_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_set_constructor
)
type_handlers.register(set)(_iter_set_instances)


_iter_frozenset_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_frozenset_constructor
)
type_handlers.register(frozenset)(_iter_frozenset_instances)


_iter_tuple_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_tuple_constructor
)
type_handlers.register(tuple)(_iter_tuple_instances)
