"""A Python module used for parameterizing Literal's and common types."""

from __future__ import annotations

import itertools
import types
from enum import Enum
from functools import partial
from typing import Any
from typing import Callable
from typing import Generator
from typing import Iterable
from typing import Mapping
from typing import Optional
from typing import Sequence
from typing import Union
from typing import get_args
from typing import get_origin

from _pytest.mark import Mark
from _pytest.python import Metafunc
from typing_extensions import Literal

from pytest_static.custom_typing import KT
from pytest_static.custom_typing import VT
from pytest_static.custom_typing import T
from pytest_static.custom_typing import T_co
from pytest_static.custom_typing import TypeHandler
from pytest_static.custom_typing import _ScopeName
from pytest_static.type_sets import predefined_type_sets


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


def get_all_possible_type_instances(type_argument: type[T]) -> tuple[T, ...]:
    """Gets all possible instances for the given type."""
    return tuple(iter_instances(type_argument))


def iter_instances(typ: Any) -> Generator[Any, None, None]:
    """Iterates over all possible instances of the given type."""
    origin: Any = get_origin(typ)
    type_args: tuple[Any, ...] = get_args(typ)
    base_type: Any = origin if origin is not None else typ

    handler: TypeHandler | partial[Generator[Any, None, None]] | None = type_handlers.get(base_type, None)

    if handler is None:
        yield from _iter_custom_instances(base_type, type_args)
    else:
        yield from handler(base_type, type_args)


def _iter_literal_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from type_args


def _iter_any_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    for typ in predefined_type_sets.keys():
        yield from iter_instances(typ)


def _iter_predefined_instances(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    yield from predefined_type_sets[base_type]


def _iter_sum_instances(_: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
    for arg in type_args:
        yield from get_all_possible_type_instances(arg)


def _iter_product_instances_with_constructor(
    _: Any,
    type_args: tuple[Any, ...],
    /,
    type_constructor: Callable[[tuple[Any, ...]], T_co],
) -> Generator[T_co, None, None]:
    if Ellipsis in type_args:
        type_args = type_args[:-1]

    combinations: Iterable[Iterable[Any]] = itertools.product(*(iter_instances(arg) for arg in type_args))
    yield from map(type_constructor, map(tuple, combinations))


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


_iter_list_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_list_constructor
)


_iter_set_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_set_constructor
)


_iter_frozenset_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_frozenset_constructor
)


_iter_tuple_instances: partial[Generator[Any, None, None]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_tuple_constructor
)


__primitive_type_handlers: dict[type[Any], TypeHandler] = {
    typ: _iter_predefined_instances for typ in predefined_type_sets.keys()
}


DEFAULT_TYPE_HANDLERS: dict[Any, TypeHandler | partial[Generator[Any, None, None]]] = {
    **__primitive_type_handlers,
    Literal: _iter_literal_instances,
    Any: _iter_any_instances,
    Union: _iter_sum_instances,
    Optional: _iter_sum_instances,
    Enum: _iter_sum_instances,
    dict: _iter_dict_instances,
    list: _iter_list_instances,
    set: _iter_set_instances,
    frozenset: _iter_frozenset_instances,
    tuple: _iter_tuple_instances,
}


type_handlers: Mapping[Any, TypeHandler | partial[Generator[Any, None, None]]] = types.MappingProxyType(
    mapping=DEFAULT_TYPE_HANDLERS
)
