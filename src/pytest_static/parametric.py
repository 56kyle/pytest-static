"""A Python module used for parameterizing Literal's and common types."""
from __future__ import annotations

import itertools
import sys
import types
import typing
from enum import Enum
from functools import partial
from typing import Any
from typing import Callable
from typing import Dict
from typing import FrozenSet
from typing import Generator
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import get_origin

from _pytest.mark import Mark
from _pytest.python import Metafunc
from typing_extensions import Literal
from typing_extensions import ParamSpec

from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS


if hasattr(typing, "_UnionGenericAlias"):
    from typing import _UnionGenericAlias  # type: ignore[attr-defined]
else:
    _UnionGenericAlias = type(Union)

if hasattr(typing, "_LiteralSpecialForm"):
    from typing import _LiteralSpecialForm  # type: ignore[attr-defined]
else:
    _LiteralSpecialForm = type(Literal)


# Redefines pytest's typing for 100% test coverage
_ScopeName = Literal["session", "package", "module", "class", "function"]

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
KT = TypeVar("KT")
VT = TypeVar("VT")
P = ParamSpec("P")

# Using algebraic data typing
SPECIAL_TYPES_SET: set[Any] = {Literal, Ellipsis, Any}
SUM_TYPES_SET: set[Any] = {Union, Optional, Enum}
PRODUCT_TYPES_SET: set[Any] = {
    List,
    list,
    Set,
    set,
    FrozenSet,
    frozenset,
    Dict,
    dict,
    Tuple,
    tuple,
}


if sys.version_info >= (3, 10):
    UNION_TYPES: set[Any] = {Union, _UnionGenericAlias, types.UnionType}
else:
    UNION_TYPES: set[Any] = {Union, _UnionGenericAlias}


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

    parameter_sets: list[list[T]] = [
        list(get_all_possible_type_instances(t)) for t in argtypes
    ]
    parameter_combinations: list[Iterable[itertools.product[tuple[Any, ...]]]] = list(
        itertools.product(*parameter_sets)
    )

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

    handler: (
        Callable[[Any, tuple[Any, ...]], Generator[Any, None, None]]
        | partial[Generator[Any, None, None]]
        | None
    ) = TYPE_HANDLERS.get(base_type, None)

    if handler is None:
        yield from _iter_custom_instances(base_type, type_args)
    else:
        yield from handler(base_type, type_args)


def _iter_literal_instances(
    base_type: Any, type_args: tuple[Any, ...]
) -> Generator[Any, None, None]:
    yield from type_args


def _iter_any_instances(
    base_type: Any, type_args: tuple[Any, ...]
) -> Generator[Any, None, None]:
    for typ in PREDEFINED_INSTANCE_SETS.keys():
        yield from iter_instances(typ)


def _iter_predefined_instances(
    base_type: Any, type_args: tuple[Any, ...]
) -> Generator[Any, None, None]:
    yield from PREDEFINED_INSTANCE_SETS[base_type]


def _iter_sum_instances(
    _: Any, type_args: tuple[Any, ...]
) -> Generator[Any, None, None]:
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

    combinations: Iterable[Iterable[Any]] = itertools.product(
        *(iter_instances(arg) for arg in type_args)
    )
    yield from map(type_constructor, map(tuple, combinations))


def _validate_combination_length(
    combination: tuple[Any, ...], expected_length: int, typ: type[Any]
) -> None:
    if len(combination) != expected_length:
        raise TypeError(
            f"Expected combination of length {expected_length} for "
            f"type {typ}. Got {len(combination)}"
        )


def _iter_custom_instances(
    base_type: Any, type_args: tuple[Any, ...]
) -> Generator[Any, None, None]:
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
    _validate_combination_length(
        combination=combination, expected_length=1, typ=frozenset
    )
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


PREDEFINED_TYPE_SET_HANDLERS: dict[
    type[Any], Callable[[Any, tuple[Any, ...]], Generator[Any, None, None]]
] = {typ: _iter_predefined_instances for typ in PREDEFINED_INSTANCE_SETS.keys()}


TYPE_HANDLERS: dict[
    Any,
    Callable[[Any, tuple[Any, ...]], Generator[Any, None, None]]
    | partial[Generator[Any, None, None]],
] = {
    **PREDEFINED_TYPE_SET_HANDLERS,
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
