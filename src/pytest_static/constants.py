"""Module containing constants used throughout the pytest-static package."""

import sys
import types
from enum import Enum
from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Literal
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union

from pytest_static.custom_typing import _UnionGenericAlias


__all__: list[str] = [
    "SPECIAL_TYPES_SET",
    "SUM_TYPES_SET",
    "PRODUCT_TYPES_SET",
    "UNION_TYPES",
]


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
