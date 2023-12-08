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


# Redefines pytest's typing for 100% test coverage
_ScopeName = Literal["session", "package", "module", "class", "function"]

T = TypeVar("T")

# Using algebraic data typing
SPECIAL_TYPES_SET: Set[Any] = {Literal, Ellipsis}
SUM_TYPES_SET: Set[Any] = {Union, Optional, Enum}
PRODUCT_TYPES_SET: Set[Any] = {
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
    """A dataclass representing a type with expanded type arguments."""

    base_type: Type[T]
    type_arguments: Tuple[Union[Any, "ExpandedType[Any]"], ...]

    @staticmethod
    def _get_combinations(argument_sets: List[Tuple[T, ...]]) -> List[Tuple[Any, ...]]:
        if len(argument_sets) > 1:
            return list(itertools.product(*argument_sets))
        return list(zip(*argument_sets))

    def get_instances(self) -> Tuple[T, ...]:
        """Gets instances of the class based on defined argument sets.

        Returns:
            instances (Tuple[T, ...]): A tuple containing the instances of the class.
        """
        argument_sets: List[Tuple[T, ...]] = self._get_argument_sets()

        combinations: List[Tuple[Any, ...]] = self._get_combinations(argument_sets)

        instances: Tuple[T, ...] = self._instantiate_combinations(combinations)
        return instances

    def _get_argument_sets(self) -> List[Tuple[T, ...]]:
        argument_instances: List[Tuple[T, ...]] = []
        for argument in self.type_arguments:
            if isinstance(argument, ExpandedType):
                argument_instances.append(argument.get_instances())
            else:
                argument_instances.append(
                    tuple(PREDEFINED_TYPE_SETS.get(argument, argument))
                )
        return argument_instances

    def _instantiate_combinations(
        self, argument_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        try:
            return self._instantiate_from_signature(argument_combinations)
        except ValueError as e:
            if "no signature found for builtin type" not in str(e):
                raise e
            return self._instantiate_error_handler(argument_combinations)

    def _instantiate_from_signature(
        self, argument_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        signature: inspect.Signature = inspect.signature(self.base_type)
        if len(signature.parameters) > 1:
            return self._handle_multiple_signature(argument_combinations)
        return self._handle_single_signature(argument_combinations)

    def _instantiate_error_handler(
        self, argument_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        try:
            return self._handle_multiple_signature(argument_combinations)
        except TypeError:
            return self._handle_single_signature(argument_combinations)

    def _handle_multiple_signature(
        self, argument_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        return tuple(
            self._instantiate_complex_type(arguments)
            for arguments in argument_combinations
        )

    def _handle_single_signature(
        self, argument_combinations: List[Tuple[Any, ...]]
    ) -> Tuple[T, ...]:
        return tuple(
            self._instantiate_basic_type(arguments)
            for arguments in argument_combinations
        )

    def _instantiate_complex_type(self, arguments: Tuple[Any, ...]) -> T:
        """Returns an instance of the base_type using the combination provided."""
        if self.base_type is dict:
            creation_method: Callable[..., T] = self.base_type
            return creation_method([arguments])
        return self.base_type(*arguments)

    def _instantiate_basic_type(self, arguments: Tuple[Any, ...]) -> T:
        creation_method: Callable[..., T] = self.base_type
        return creation_method(arguments)


@dataclass(frozen=True)
class Config:
    """A dataclass used to configure the expansion of types."""

    max_elements_count: int = 5
    max_recursion_depth: int = 5
    type_handlers: Dict[
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

    parameter_sets: List[List[T]] = [
        list(get_all_possible_type_instances(t)) for t in argtypes
    ]
    parameter_combinations: List[Iterable[itertools.product[Tuple[Any, ...]]]] = list(
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


def get_all_possible_type_instances(
    type_argument: Type[T], config: Config = DEFAULT_CONFIG
) -> Tuple[T, ...]:
    """Gets all possible instances for the given type.

    Args:
        type_argument: The type argument for which to generate all possible instances.
        config: The configuration for expanding types. Default is `DEFAULT_CONFIG`.

    Returns:
        A tuple containing all possible instances of the specified type.
    """
    expanded_types: Set[Union[Any, ExpandedType[T]]] = expand_type(
        type_argument, config
    )
    instances: List[T] = []
    for expanded_type in expanded_types:
        if isinstance(expanded_type, ExpandedType):
            instances.extend(expanded_type.get_instances())
        else:
            instances.extend(PREDEFINED_TYPE_SETS.get(expanded_type, []))
    return tuple(instances)


def _ensure_sequence(value: Union[str, Sequence[str]]) -> Sequence[str]:
    if isinstance(value, str):
        return value.split(", ")
    return value


def return_self(argument: T, *_: Any) -> Set[T]:
    """Returns a set containing the argument.

    Args:
        argument: The argument to be returned in a set.

    Returns:
        Set[T]: Set containing the argument.
    """
    return {argument}


def expand_type(
    type_argument: Type[T], config: Config = DEFAULT_CONFIG
) -> Set[ExpandedType[T]]:
    """Expands the provided type into a set of ExpandedType instances.

    Args:
        type_argument (Type[T]): The type to expand.
        config (Config): The configuration for expanding types.

    Returns:
        Set[ExpandedType[T]]: A set of expanded types.
    """
    original_type: Any = get_origin(type_argument)
    base_type: Any = original_type if original_type is not None else type_argument

    if base_type in PREDEFINED_TYPE_SETS:
        return {base_type}

    type_handlers: Dict[Any, Callable[[Type[T], Config], Set[ExpandedType[T]]]] = {
        Literal: return_self,
        Ellipsis: return_self,
        **{sum_type: expand_sum_type for sum_type in SUM_TYPES_SET},
        **{product_type: expand_product_type for product_type in PRODUCT_TYPES_SET},
    }

    # Add custom handlers from configuration
    type_handlers.update(config.type_handlers)

    if base_type in type_handlers:
        return type_handlers[base_type](type_argument, config)

    return {type_argument}


def expand_sum_type(type_argument: Type[T], config: Config) -> Set[ExpandedType[T]]:
    """Expands a sum type by expanding each argument of the type.

    Args:
        type_argument (Type[T]): The sum type to be expanded.
        config (Config): The configuration object.

    Returns:
        Set[ExpandedType[T]]: A set of expanded types.
    """
    return {
        *itertools.chain.from_iterable(
            expand_type(argument, config) for argument in get_args(type_argument)
        )
    }


def expand_product_type(type_argument: Type[T], config: Config) -> Set[ExpandedType[T]]:
    """Expands a product type into a set of ExpandedType instances.

    This function expands a given type (Type[T]) that is assumed to be a product
    type - a type defined as a combination of other types. Examples of product
    types include Tuple or custom data classes.

    The function generates a set of 'ExpandedType' objects for the input
    type_argument. The set is derived by all possible combinations (Cartesian
    product) of expanded subtypes, based on the rules in the input config.

    Args:
        type_argument (Type[T]): The product type to expand.
        config (Config): Input Config object that specifies the rules for the
        type expansion.

    Returns:
        Set[ExpandedType[T]]: A set of ExpandedType objects that represents all
        possible instances of the original type.
    """
    original_type: Any = get_origin(type_argument) or type_argument
    subtypes: Tuple[Any, ...] = get_args(type_argument)
    expanded_subtypes: List[Set[ExpandedType[T]]] = [
        expand_type(argument, config) for argument in subtypes
    ]
    product_sets: Tuple[Iterable[ExpandedType[T]], ...] = tuple(
        itertools.product(*expanded_subtypes)
    )
    return {
        ExpandedType(original_type, tuple(product_set)) for product_set in product_sets
    }
