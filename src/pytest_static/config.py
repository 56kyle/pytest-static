"""A config for providing custom type expansion handlers."""
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from typing import Callable
from typing import Dict
from typing import Set
from typing import Type
from typing import Union

from pytest_static.parametric import ExpandedType
from pytest_static.parametric import T


@dataclass(frozen=True)
class Config:
    """A dataclass used to configure the expansion of types."""

    max_elements: int = 5
    max_depth: int = 5
    custom_handlers: Dict[
        Any, Callable[[Type[T], "Config"], Set[Union[Any, ExpandedType[T]]]]
    ] = field(default_factory=dict)
