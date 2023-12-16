"""A Python module used for parameterizing Literal's and common types."""
from __future__ import annotations

import inspect
import itertools
import types
import typing
from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import FrozenSet
from typing import Generic
from typing import Iterable
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import TypeVar
from typing import Union
from typing import _SpecialForm
from typing import cast
from typing import get_args
from typing import get_origin
from typing import overload

from _pytest.mark import Mark
from _pytest.python import Metafunc
from typing_extensions import Literal
from typing_extensions import ParamSpec

from pytest_static.exceptions import ExpandedTypeNotCallableError
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
SPECIAL_TYPES_SET: set[Any] = {Literal, Ellipsis}
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


@dataclass(frozen=True)
class ExpandedType(Generic[T_co]):
    """A dataclass representing a type with expanded type arguments."""

    base_type: T_co
    type_arguments: tuple[Any, ...]

    @staticmethod
    def _get_combinations(
        argument_sets: list[tuple[Any, ...]]
    ) -> list[tuple[Any, ...]]:
        if len(argument_sets) > 1:
            return list(itertools.product(*argument_sets))
        return list(zip(*argument_sets))

    def get_instances(self) -> tuple[Any, ...]:
        """Gets instances of the class based on defined argument sets.

        Returns:
            instances: A tuple containing the instances of the class.
        """
        if self.base_type in PREDEFINED_INSTANCE_SETS.keys():
            return tuple(PREDEFINED_INSTANCE_SETS[self.base_type])

        if self.base_type is Literal:
            return self.type_arguments

        argument_sets: list[tuple[T_co, ...]] = self._get_argument_sets()

        combinations: list[tuple[Any, ...]] = self._get_combinations(argument_sets)

        instances: tuple[T_co, ...] = self._instantiate_combinations(combinations)
        return instances

    def _casted_base_type_as_callable(self) -> Callable[..., T_co]:
        self._ensure_base_type_callable()
        return cast(Callable[..., T_co], self.base_type)

    def _ensure_base_type_callable(self) -> None:
        if not callable(self.base_type):
            raise ExpandedTypeNotCallableError(self.base_type)

    def _get_argument_sets(self) -> list[tuple[T_co, ...]]:
        argument_instances: list[tuple[T_co, ...]] = []
        for argument in self.type_arguments:
            if isinstance(argument, ExpandedType):
                argument_instances.append(argument.get_instances())
            else:
                argument_instances.append(
                    tuple(PREDEFINED_INSTANCE_SETS.get(argument, argument))
                )
        return argument_instances

    def _instantiate_combinations(
        self, argument_combinations: list[tuple[Any, ...]]
    ) -> tuple[T_co, ...]:
        try:
            return self._instantiate_from_signature(argument_combinations)
        except ValueError as e:
            if "no signature found for builtin type" not in str(e):
                raise e
            return self._instantiate_error_handler(argument_combinations)

    def _instantiate_from_signature(
        self, argument_combinations: list[tuple[Any, ...]]
    ) -> tuple[T_co, ...]:
        creation_method: Callable[..., T_co] = self._casted_base_type_as_callable()
        signature: inspect.Signature = inspect.signature(creation_method)
        if len(signature.parameters) > 1:
            return self._handle_multiple_signature(argument_combinations)
        return self._handle_single_signature(argument_combinations)

    def _instantiate_error_handler(
        self, argument_combinations: list[tuple[Any, ...]]
    ) -> tuple[T_co, ...]:
        try:
            return self._handle_multiple_signature(argument_combinations)
        except TypeError:
            return self._handle_single_signature(argument_combinations)

    def _handle_multiple_signature(
        self, argument_combinations: list[tuple[Any, ...]]
    ) -> tuple[T_co, ...]:
        return tuple(
            self._instantiate_complex_type(arguments)
            for arguments in argument_combinations
        )

    def _handle_single_signature(
        self, argument_combinations: list[tuple[Any, ...]]
    ) -> tuple[T_co, ...]:
        return tuple(
            self._instantiate_basic_type(arguments)
            for arguments in argument_combinations
        )

    def _instantiate_complex_type(self, arguments: tuple[Any, ...]) -> T_co:
        """Returns an instance of the base_type using the combination provided."""
        creation_method: Callable[..., T_co] = self._casted_base_type_as_callable()
        if self.base_type is dict:
            return creation_method([arguments])
        return creation_method(*arguments)

    def _instantiate_basic_type(self, arguments: tuple[Any, ...]) -> T_co:
        creation_method: Callable[..., T_co] = self._casted_base_type_as_callable()
        return creation_method(arguments)


def parametrize_types(
    metafunc: Metafunc,
    argnames: str | Sequence[str],
    argtypes: list[type[T]],
    indirect: bool | Sequence[str] = False,
    ids: None | (Iterable[object | None] | Callable[[Any], object | None]) = None,
    scope: _ScopeName | None = None,
    *,
    _param_mark: Mark | None = None,
) -> None:
    """Pytest marker emulating pytest parametrize but using types to specify sets.

    Args:
        metafunc: The pytest metafunc object. Used to parameterize the test
                  function.
        argnames: The names of the arguments to be parametrized.
        argtypes: The types of the arguments to be parametrized.
        indirect: Whether the arguments should be passed as indirect fixtures
                  to the test function.
        ids: Optional. The ids to use for each parameter combination. Generated
             as comma-separated lists of the parameter values if not provided.
        scope: Optional. The scope of the parameterization. Defaults to
               "function" scope if not provided.
        _param_mark: Optional. The pytest mark to add to the parameterized
                     test function.
    """
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


def get_all_possible_type_instances(type_argument: type[T]) -> tuple[T, ...]:
    """Gets all possible instances for the given type.

    Args:
        type_argument: The type argument for which to generate all possible instances.

    Returns:
        A tuple containing all possible instances of the specified type.
    """
    expanded_types: set[type[T] | ExpandedType[T]] = expand_type(type_argument)
    instances: list[T] = []
    for expanded_type in expanded_types:
        if isinstance(expanded_type, ExpandedType):
            instances.extend(expanded_type.get_instances())
        else:
            instances.extend(PREDEFINED_INSTANCE_SETS.get(expanded_type, []))
    return tuple(instances)


def _ensure_sequence(value: str | Sequence[str]) -> Sequence[str]:
    if isinstance(value, str):
        return value.split(", ")
    return value


@overload
def expand_type(type_argument: type[_LiteralSpecialForm]) -> set[Any]:
    ...


@overload
def expand_type(
    type_argument: type[_UnionGenericAlias]
    | _UnionGenericAlias
    | type[types.UnionType]
    | types.UnionType,
) -> set[Any]:
    ...


@overload
def expand_type(type_argument: Enum) -> set[ExpandedType[Enum]]:
    ...


@overload
def expand_type(
    type_argument: type[dict[KT, VT]]
) -> set[ExpandedType[type[dict[KT, VT]]]]:
    ...


@overload
def expand_type(type_argument: type[T]) -> set[ExpandedType[type[T]] | type[T]]:
    ...


def expand_type(type_argument: Any) -> set[Any]:
    """Expands the provided type into a set of ExpandedType instances.

    Args:
        type_argument: The type to expand.

    Returns:
        A set of expanded types.
    """
    original_type: Any = get_origin(type_argument)
    base_type: Any = original_type if original_type is not None else type_argument

    if base_type in TYPE_HANDLERS:
        return TYPE_HANDLERS[base_type](type_argument)

    return {ExpandedType(base_type=type_argument, type_arguments=tuple())}


def expand_literal_type(
    type_argument: type[_SpecialForm],
) -> set[ExpandedType[Any]]:
    """Expands the provided Literal type.

    Args:
        type_argument: The literal type to expand.

    Returns:
        A set of expanded types.
    """
    return {
        ExpandedType(base_type=type_argument, type_arguments=get_args(type_argument))
    }


def expand_basic_type(
    type_argument: type[T],
) -> set[type[T]]:
    """Expands a basic type by just returning said type in a set.

    Args:
        type_argument: The basic type that needs to be expanded.

    Returns:
        A set containing just the basic type that was given.
    """
    return {type_argument}


@overload
def expand_sum_type(type_argument: type[_SpecialForm]) -> set[ExpandedType[Any]]:
    ...


@overload
def expand_sum_type(type_argument: Enum) -> set[ExpandedType[Enum]]:
    ...


def expand_sum_type(type_argument: Any) -> set[Any]:
    """Expands a sum type by expanding each argument of the type.

    Args:
        type_argument: The sum type to be expanded.

    Returns:
        A set of expanded types.
    """
    return {
        *itertools.chain.from_iterable(
            expand_type(argument) for argument in get_args(type_argument)
        )
    }


@overload
def expand_product_type(type_argument: type[T]) -> set[ExpandedType[T]]:
    ...


@overload
def expand_product_type(type_argument: object) -> set[ExpandedType[Any]]:
    ...


def expand_product_type(type_argument: Any) -> set[ExpandedType[Any]]:
    """Expands a product type into a set of ExpandedType instances.

    This function expands a given type (Type[T]) that is assumed to be a product
    type - a type defined as a combination of other types. Examples of product
    types include Tuple or custom data classes.

    The function generates a set of 'ExpandedType' objects for the input
    type_argument. The set is derived by all possible combinations (Cartesian
    product) of expanded subtypes.

    Args:
        type_argument: The product type to expand.

    Returns:
        A set of ExpandedType objects that represents all possible instances of
        the original type.
    """
    original_type: Any = get_origin(type_argument) or type_argument
    subtypes: tuple[Any, ...] = get_args(type_argument)
    expanded_subtypes: list[set[Any]] = [expand_type(argument) for argument in subtypes]
    product_sets: tuple[Iterable[Any], ...] = tuple(
        itertools.product(*expanded_subtypes)
    )
    return {
        ExpandedType(original_type, tuple(product_set)) for product_set in product_sets
    }


TYPE_HANDLERS: dict[Any, Callable[..., set[Any]]] = {
    Literal: expand_literal_type,
    **{basic_type: expand_basic_type for basic_type in PREDEFINED_INSTANCE_SETS},
    **{sum_type: expand_sum_type for sum_type in SUM_TYPES_SET},
    **{product_type: expand_product_type for product_type in PRODUCT_TYPES_SET},
}
