"""A Python module used for parameterizing Literal's and common types."""

from __future__ import annotations

import itertools
from enum import Enum
from functools import partial
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import Optional
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import get_type_hints

from typing_extensions import Literal
from typing_extensions import is_protocol

from pytest_static.type_handler import TypeHandlerRegistry
from pytest_static.type_sets import BOOL_PARAMS
from pytest_static.type_sets import BYTES_PARAMS
from pytest_static.type_sets import COMPLEX_PARAMS
from pytest_static.type_sets import DEFAULT_INSTANCE_SETS
from pytest_static.type_sets import FLOAT_PARAMS
from pytest_static.type_sets import INT_PARAMS
from pytest_static.type_sets import STR_PARAMS
from pytest_static.util import get_base_type


if TYPE_CHECKING:
    from collections.abc import Generator
    from collections.abc import Iterable
    from collections.abc import Sequence

    from _pytest.mark import Mark
    from _pytest.python import Metafunc

    from pytest_static.custom_typing import KT
    from pytest_static.custom_typing import VT
    from pytest_static.custom_typing import T
    from pytest_static.custom_typing import T_co
    from pytest_static.custom_typing import TypeConstructor
    from pytest_static.custom_typing import TypeHandler
    from pytest_static.custom_typing import _ScopeName


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


def iter_instances(key: Any, handler_registry: TypeHandlerRegistry = type_handlers) -> Generator[Any]:
    """Returns a Generator that yields from all handlers."""
    base_type: Any = get_base_type(key)
    type_args: tuple[Any, ...] = get_args(key)

    fallback_handlers: Iterable[TypeHandler] = [_iter_instances_using_fallback]
    handlers: Iterable[TypeHandler] = handler_registry.get(base_type, fallback_handlers)

    for handler in handlers:
        yield from handler(base_type, type_args)


def _iter_instances_using_fallback(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any]:
    """Returns a Generator that yields from default fallback methods for the given base_type and type_args."""
    if isinstance(base_type, TypeVar):
        yield from _iter_type_var_instances(base_type, type_args)
    elif is_protocol(base_type):
        yield from _iter_protocol_instances(base_type, type_args)
    elif callable(base_type):
        yield from _iter_callable_instances(base_type, type_args)
    else:
        raise TypeError(f"Failed to find a fallback method for instantiating {base_type=}.")


def _iter_type_var_instances(base_type: Any, _: tuple[Any, ...], **__: Any) -> Generator[Any]:
    if base_type.__constraints__:
        for constraint in base_type.__constraints__:
            yield from get_all_possible_type_instances(constraint)
    elif base_type.__bound__:
        yield from get_all_possible_type_instances(base_type.__bound__)
    else:
        yield from get_all_possible_type_instances(Any)


def _iter_callable_instances(base_type: Any, _: tuple[Any, ...], **__: Any) -> Generator[Any]:
    type_hints: dict[str, Any] = get_type_hints(base_type)
    type_annotations: tuple[Any, ...] = tuple(v for k, v in type_hints.items() if k != "return")
    yield from _iter_product_instances_with_constructor(base_type, type_annotations, type_constructor=base_type)


def _iter_protocol_instances(*_: Any, **__: Any) -> Generator[Any]:
    raise NotImplementedError


@type_handlers.register(type(None))  # pragma: no cover
def _iter_none_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield None


@type_handlers.register(bool)  # pragma: no cover
def _iter_bool_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from BOOL_PARAMS


@type_handlers.register(int)  # pragma: no cover
def _iter_int_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from INT_PARAMS


@type_handlers.register(float)  # pragma: no cover
def _iter_float_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from FLOAT_PARAMS


@type_handlers.register(complex)  # pragma: no cover
def _iter_complex_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from COMPLEX_PARAMS


@type_handlers.register(str)  # pragma: no cover
def _iter_str_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from STR_PARAMS


@type_handlers.register(bytes)  # pragma: no cover
def _iter_bytes_instances(*_: Any, **__: Any) -> Generator[Any]:
    yield from BYTES_PARAMS


@type_handlers.register(Literal)  # pragma: no cover
def _iter_literal_instances(_: Any, type_args: tuple[Any, ...], **__: Any) -> Generator[Any]:
    yield from type_args


@type_handlers.register(Any)  # pragma: no cover
def _iter_any_instances(*_: Any) -> Generator[Any]:
    for typ in DEFAULT_INSTANCE_SETS:
        yield from get_all_possible_type_instances(typ)


@type_handlers.register(Union, Optional, Enum)  # pragma: no cover
def _iter_sum_instances(_: Any, type_args: tuple[Any, ...]) -> Generator[Any]:
    for arg in type_args:
        yield from get_all_possible_type_instances(arg)


def _iter_combinations(type_args: tuple[Any, ...]) -> Generator[tuple[Any, ...]]:
    yield from itertools.product(*map(get_all_possible_type_instances, type_args))


def _iter_product_instances_with_constructor(
    _: Any,
    type_args: tuple[Any, ...],
    /,
    type_constructor: TypeConstructor[T_co],
) -> Generator[T_co]:
    if Ellipsis in type_args:
        type_args = type_args[:-1]
    yield from itertools.starmap(type_constructor, _iter_combinations(type_args))


def _validate_combination_length(combination: tuple[Any, ...], expected_length: int, typ: type[Any]) -> None:
    if len(combination) != expected_length:
        raise TypeError(f"Expected combination of length {expected_length} for type {typ}. Got {len(combination)}")


def _dict_constructor(k: KT, v: VT) -> dict[KT, VT]:
    return {k: v}


def _list_constructor(value: T) -> list[T]:
    return [value]


def _set_constructor(value: T) -> set[T]:
    _validate_combination_length(combination=(value,), expected_length=1, typ=set)
    return {value}


def _frozenset_constructor(*args: Any) -> frozenset[Any]:
    _validate_combination_length(combination=args, expected_length=1, typ=frozenset)
    return frozenset(args)


def _tuple_constructor(*args: Any) -> tuple[Any, ...]:
    return tuple(args)


_iter_dict_instances: partial[Generator[Any]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_dict_constructor
)
type_handlers.register(dict)(_iter_dict_instances)  # pragma: no cover


_iter_list_instances: partial[Generator[Any]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_list_constructor
)
type_handlers.register(list)(_iter_list_instances)  # pragma: no cover


_iter_set_instances: partial[Generator[Any]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_set_constructor
)
type_handlers.register(set)(_iter_set_instances)  # pragma: no cover


_iter_frozenset_instances: partial[Generator[Any]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_frozenset_constructor
)
type_handlers.register(frozenset)(_iter_frozenset_instances)  # pragma: no cover


_iter_tuple_instances: partial[Generator[Any]] = partial(
    _iter_product_instances_with_constructor, type_constructor=_tuple_constructor
)
type_handlers.register(tuple)(_iter_tuple_instances)  # pragma: no cover
