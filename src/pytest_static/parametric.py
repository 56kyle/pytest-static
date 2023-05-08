"""A Python module used for parameterizing Literal's and common types."""
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

from _pytest.python import Metafunc

from pytest_static.type_sets import PREDEFINED_TYPE_SETS


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

    def get_instances(self) -> Tuple[T, ...]:
        """Returns a tuple of all possible instances of the primary_type."""
        type_sets: List[Tuple[T, ...]] = []
        for arg in self.type_args:
            if isinstance(arg, ExpandedType):
                type_sets.append(arg.get_instances())
            else:
                type_sets.append(PREDEFINED_TYPE_SETS.get(arg, arg))
        instances: List[T] = list(
            self.primary_type(*args) for args in itertools.product(*type_sets)
        )
        return tuple(instances)


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
    ids: Optional[Union[Sequence[str], Callable]] = None,
    *args,
    **kwargs
) -> None:
    """Parametrizes the provided argnames with the provided argtypes."""
    argnames = _ensure_sequence(argnames)
    if len(argnames) != len(argtypes):
        raise ValueError("The number of argnames and argtypes must be the same.")

    expanded_types = [expand_type(t) for t in argtypes]
    type_sets = [list(et) for et in expanded_types]

    # Get instances for each type set
    instance_sets = []
    for ts in type_sets:
        instances = []
        for t in ts:
            if isinstance(t, ExpandedType):
                instances.extend(t.get_instances())
            else:
                instances.extend(PREDEFINED_TYPE_SETS.get(t, []))
        instance_sets.append(instances)

    instance_combinations = list(itertools.product(*instance_sets))

    if ids is None:
        ids = [", ".join(map(repr, ic)) for ic in instance_combinations]

    metafunc.parametrize(argnames, instance_combinations, ids=ids, *args, **kwargs)


def _ensure_sequence(value: Union[str, Sequence[str]]) -> Sequence[str]:
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
