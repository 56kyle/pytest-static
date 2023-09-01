"""A Python module used for parameterizing Literal's and common types."""
import inspect
import itertools
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Callable
from typing import Dict
from typing import FrozenSet
from typing import Generic
from typing import Iterable
from typing import List
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import get_origin

from _pytest.mark import Mark
from _pytest.python import Metafunc

from pytest_static.type_sets import PREDEFINED_TYPE_SETS


# Redefines pytest's typing so that we can get 100% test coverage
_ScopeName = Literal["session", "package", "module", "class", "function"]

T = TypeVar("T")


DEFAULT_SUM_TYPES: Set[Any] = {Union, Optional, Enum}
DEFAULT_PRODUCT_TYPES: Set[Any] = {
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
class ExpandedType(Generic[T]):
    """A dataclass used to represent a type with expanded type arguments."""

    primary_type: Type[T]
    type_args: Tuple[Union[Any, "ExpandedType[Any]"], ...]

    @staticmethod
    def _get_parameter_combinations(
        parameter_instance_sets: List[Tuple[T, ...]]
    ) -> List[Tuple[Any, ...]]:
        """Returns a list of parameter combinations."""
        if len(parameter_instance_sets) > 1:
            return list(itertools.product(*parameter_instance_sets))
        return list(zip(*parameter_instance_sets))

    def get_instances(self) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        parameter_instance_sets: List[
            Tuple[T, ...]
        ] = self._get_parameter_instance_sets()

        parameter_combinations: List[
            Tuple[Any, ...]
        ] = self._get_parameter_combinations(parameter_instance_sets)

        instances: Tuple[T, ...] = self._instantiate_each_parameter_combination(
            parameter_combinations
        )
        return instances

    def _get_parameter_instance_sets(self) -> List[Tuple[T, ...]]:
        """Returns a list of parameter instance sets."""
        parameter_instances: List[Tuple[T, ...]] = []
        for arg in self.type_args:
            if isinstance(arg, ExpandedType):
                parameter_instances.append(arg.get_instances())
            else:
                parameter_instances.append(tuple(PREDEFINED_TYPE_SETS.get(arg, arg)))
        return parameter_instances

    def _instantiate_each_parameter_combination(
        self, parameter_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        try:
            return self._instantiate_from_signature(parameter_combinations)
        except ValueError as e:
            if "no signature found for builtin type" not in str(e):
                raise e
            return self._instantiate_from_trial_and_error(parameter_combinations)

    def _instantiate_from_signature(
        self, parameter_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        signature: inspect.Signature = inspect.signature(self.primary_type)
        if len(signature.parameters) > 1:
            return self._instantiate_combinations_using_expanded(
                parameter_combinations=parameter_combinations
            )
        return self._instantiate_combinations_using_not_expanded(
            parameter_combinations=parameter_combinations
        )

    def _instantiate_from_trial_and_error(
        self, parameter_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        try:
            return self._instantiate_combinations_using_expanded(
                parameter_combinations=parameter_combinations
            )
        except TypeError:
            return self._instantiate_combinations_using_not_expanded(
                parameter_combinations=parameter_combinations
            )

    def _instantiate_combinations_using_expanded(
        self, parameter_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        return tuple(self._instantiate_expanded(pc) for pc in parameter_combinations)

    def _instantiate_combinations_using_not_expanded(
        self, parameter_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        return tuple(
            self._instantiate_not_expanded(pc) for pc in parameter_combinations
        )

    def _instantiate_expanded(self, combination: Tuple[Any, ...]) -> T:
        """Returns an instance of the primary_type using the combination provided."""
        if self.primary_type is dict:
            instantiation_method: Callable[..., T] = self.primary_type
            return instantiation_method([combination])
        return self.primary_type(*combination)

    def _instantiate_not_expanded(self, combination: Tuple[Any, ...]) -> T:
        """Returns an instance of the primary_type using the combination provided."""
        instantiation_method: Callable[..., T] = self.primary_type
        return instantiation_method(combination)


@dataclass(frozen=True)
class Config:
    """A dataclass used to configure the expansion of types."""

    max_elements: int = 5
    max_depth: int = 5
    custom_handlers: Dict[
        Any, Callable[[Type[T], "Config"], Set[Union[Any, ExpandedType[T]]]]
    ] = field(default_factory=dict)


DEFAULT_CONFIG: Config = Config()


def parametrize_types(
    metafunc: Metafunc,
    argnames: Union[str, Sequence[str]],
    argtypes: List[Type[T]],
    indirect: Union[bool, Sequence[str]] = False,
    ids: Optional[
        Union[Iterable[Optional[object]], Callable[[Any], Optional[object]]]
    ] = None,
    scope: Optional[_ScopeName] = None,
    *,
    _param_mark: Optional[Mark] = None,
) -> None:
    """Parametrizes the provided argnames with the provided argtypes."""
    argnames = _ensure_sequence(argnames)
    if len(argnames) != len(argtypes):
        raise ValueError("The number of argnames and argtypes must be the same.")

    instance_sets: List[List[T]] = [
        list(get_all_possible_type_instances(t)) for t in argtypes
    ]
    instance_combinations: List[Iterable[itertools.product[Tuple[Any, ...]]]] = list(
        itertools.product(*instance_sets)
    )

    if ids is None:
        ids = [", ".join(map(repr, ic)) for ic in instance_combinations]

    metafunc.parametrize(
        argnames=argnames,
        argvalues=instance_combinations,
        indirect=indirect,
        ids=ids,
        scope=scope,
        _param_mark=_param_mark,
    )


def get_all_possible_type_instances(
    type_arg: Type[T], config: Config = DEFAULT_CONFIG
) -> Tuple[T, ...]:
    """Returns a tuple of all possible instances of the provided type."""
    expanded_types: Set[Union[Any, ExpandedType[T]]] = expand_type(type_arg, config)
    instances: List[T] = []
    for expanded_type in expanded_types:
        if isinstance(expanded_type, ExpandedType):
            instances.extend(expanded_type.get_instances())
        else:
            instances.extend(PREDEFINED_TYPE_SETS.get(expanded_type, []))
    return tuple(instances)


def _ensure_sequence(value: Union[str, Sequence[str]]) -> Sequence[str]:
    """Returns the provided value as a sequence."""
    if isinstance(value, str):
        return value.split(", ")
    return value


def return_self(arg: T, *_: Any) -> Set[T]:
    """Returns the provided argument."""
    return {arg}


def expand_type(
    type_arg: Union[Any, Type[T]], config: Config = DEFAULT_CONFIG
) -> Set[Union[Any, ExpandedType[T]]]:
    """Expands the provided type into the set of all possible subtype combinations."""
    origin: Any = get_origin(type_arg) or type_arg

    if origin in PREDEFINED_TYPE_SETS:
        return {origin}

    type_handlers: Dict[
        Any, Callable[[Type[T], Config], Set[Union[Any, ExpandedType[T]]]]
    ] = {
        Literal: return_self,
        Ellipsis: return_self,
        **{sum_type: expand_sum_type for sum_type in DEFAULT_SUM_TYPES},
        **{product_type: expand_product_type for product_type in DEFAULT_PRODUCT_TYPES},
    }

    # Add custom handlers from configuration
    type_handlers.update(config.custom_handlers)

    if origin in type_handlers:
        return type_handlers[origin](type_arg, config)

    return {type_arg}


def expand_sum_type(
    type_arg: Type[T], config: Config
) -> Set[Union[Any, ExpandedType[T]]]:
    """Expands a sum type into the set of all possible subtype combinations."""
    return {
        *itertools.chain.from_iterable(
            expand_type(arg, config) for arg in get_args(type_arg)
        )
    }


def expand_product_type(
    type_arg: Type[T], config: Config
) -> Set[Union[Any, ExpandedType[T]]]:
    """Expands a product type into the set of all possible subtype combinations."""
    origin: Any = get_origin(type_arg) or type_arg
    args: Tuple[Any, ...] = get_args(type_arg)
    sets: List[Set[Union[Any, ExpandedType[T]]]] = [
        expand_type(arg, config) for arg in args
    ]
    product_sets: Tuple[Iterable[Union[Any, ExpandedType[T]]], ...] = tuple(
        itertools.product(*sets)
    )
    return {ExpandedType(origin, tuple(product_set)) for product_set in product_sets}
