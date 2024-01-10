"""Common utility functions and info for pytest-static tests."""
from __future__ import annotations

import sys
from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Literal
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import get_args
from typing import get_origin

from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS


# Predefined Instance Set Lengths
BOOL_LEN: int = len(PREDEFINED_INSTANCE_SETS[bool])
INT_LEN: int = len(PREDEFINED_INSTANCE_SETS[int])
FLOAT_LEN: int = len(PREDEFINED_INSTANCE_SETS[float])
COMPLEX_LEN: int = len(PREDEFINED_INSTANCE_SETS[complex])
STR_LEN: int = len(PREDEFINED_INSTANCE_SETS[str])
BYTES_LEN: int = len(PREDEFINED_INSTANCE_SETS[bytes])
NONE_LEN: int = 1
ELLIPSIS_LEN: int = 0


SPECIAL_TYPE_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Literal[1, 2, 3], 3),
    (Literal[1, Literal[2, 3]], 3),
    (Literal[1, Literal[Literal[2, 3], Literal[4, 5]]], 5),
    (Literal[1, Literal[Literal[1, 2], Literal[2, 3], Literal[3, 4]]], 4),
]


BASIC_TYPE_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (bool, BOOL_LEN),
    (int, INT_LEN),
    (float, FLOAT_LEN),
    (complex, COMPLEX_LEN),
    (str, STR_LEN),
    (bytes, BYTES_LEN),
]


SUM_TYPE_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Union[bool, int], BOOL_LEN + INT_LEN),
    (Optional[int], INT_LEN + NONE_LEN),
    (Union[bool, Union[int, str]], BOOL_LEN + INT_LEN + STR_LEN),
    (Optional[Union[int, str]], INT_LEN + STR_LEN + NONE_LEN),
]


PRODUCT_TYPE_MISSING_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (List, -1),
    (list, -1),
    (Set, -1),
    (set, -1),
    (FrozenSet, -1),
    (frozenset, -1),
]


PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (List[int], INT_LEN),
    (Set[int], INT_LEN),
    (FrozenSet[int], INT_LEN),
]


if sys.version_info >= (3, 9):
    PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES_POST_39: list[tuple[Any, int]] = [
        (list[int], INT_LEN),  # type: ignore[misc]
        (set[int], INT_LEN),  # type: ignore[misc]
        (frozenset[int], INT_LEN),  # type: ignore[misc]
    ]
    PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES.extend(
        PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES_POST_39
    )


PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Dict[bool, int], BOOL_LEN * INT_LEN),
    (Dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),
]


if sys.version_info >= (3, 9):
    PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES_POST_39: list[tuple[Any, int]] = [
        (dict[bool, int], BOOL_LEN * INT_LEN),  # type: ignore[misc]
        (dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),  # type: ignore[misc]
    ]
    PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES.extend(
        PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES_POST_39
    )

PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),
    (
        Tuple[Union[bool, int], int, Union[bool, str]],
        (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN),
    ),
]


if sys.version_info >= (3, 9):
    PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES_POST_39: list[tuple[Any, int]] = [
        (tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),  # type: ignore[misc]
        (
            tuple[Union[bool, int], int, Union[bool, str]],  # type: ignore[misc]
            (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN),
        ),
    ]
    PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES.extend(
        PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES_POST_39
    )


PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[int, ...], INT_LEN),
    (Tuple[Union[int, str], ...], INT_LEN + STR_LEN),
]


if sys.version_info >= (3, 9):
    PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES_POST_39: list[tuple[Any, int]] = [
        (tuple[int, ...], INT_LEN),  # type: ignore[misc]
        (tuple[Union[int, str], ...], INT_LEN + STR_LEN),  # type: ignore[misc]
    ]
    PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES.extend(
        PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES_POST_39
    )


PRODUCT_TYPE_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    *PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES,
    *PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES,
    *PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES,
    *PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES,
]


def type_annotation_to_string(annotation: Any) -> str:
    """Takes a type annotation and returns a str that can create it in code.

    Arguments:
        annotation: A type annotation.

    Returns:
        The string representation of the type annotation.
    """
    origin: Any = get_origin(annotation)
    args: tuple[Any, ...] = get_args(annotation)
    args_str: str = ", ".join(type_annotation_to_string(arg) for arg in args)

    if annotation in [None, type(None)]:
        return "None"
    elif isinstance(annotation, type):
        return (
            f"{annotation.__name__}[{args_str}]" if args else str(annotation.__name__)
        )
    elif origin is not None:
        origin_name: str = getattr(origin, "__name__", str(origin))
        return f"{origin_name}[{args_str}]" if args else origin_name
    else:
        return str(annotation)
