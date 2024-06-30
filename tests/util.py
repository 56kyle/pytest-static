"""Common utility functions and info for pytest-static tests."""

from __future__ import annotations

from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import _SpecialGenericAlias  # type: ignore[attr-defined]

from typing_extensions import Literal
from typing_extensions import get_args
from typing_extensions import get_origin

from pytest_static.type_sets import DEFAULT_INSTANCE_SETS


# Predefined Instance Set Lengths
BOOL_LEN: int = len(DEFAULT_INSTANCE_SETS[bool])
INT_LEN: int = len(DEFAULT_INSTANCE_SETS[int])
FLOAT_LEN: int = len(DEFAULT_INSTANCE_SETS[float])
COMPLEX_LEN: int = len(DEFAULT_INSTANCE_SETS[complex])
STR_LEN: int = len(DEFAULT_INSTANCE_SETS[str])
BYTES_LEN: int = len(DEFAULT_INSTANCE_SETS[bytes])
NONE_LEN: int = 1
ELLIPSIS_LEN: int = 0
ANY_LEN: int = BOOL_LEN + INT_LEN + FLOAT_LEN + COMPLEX_LEN + STR_LEN + BYTES_LEN + NONE_LEN + ELLIPSIS_LEN


SPECIAL_TYPE_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Literal[1, 2, 3], 3),
    (Literal[1, Literal[2, 3]], 3),
    (Literal[1, Literal[Literal[2, 3], Literal[4, 5]]], 5),
    (Literal[1, Literal[Literal[1, 2], Literal[2, 3], Literal[3, 4]]], 4),
    (Any, ANY_LEN),
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
    (list[int], INT_LEN),
    (set[int], INT_LEN),
    (frozenset[int], INT_LEN),
]


PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Dict[bool, int], BOOL_LEN * INT_LEN),
    (Dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),
    (dict[bool, int], BOOL_LEN * INT_LEN),
    (dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),
]


PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),
    (Tuple[Union[bool, int], int, Union[bool, str]], (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN)),
    (tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),
    (tuple[Union[bool, int], int, Union[bool, str]], (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN)),
]


PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[int, ...], INT_LEN),
    (Tuple[Union[int, str], ...], INT_LEN + STR_LEN),
    (tuple[int, ...], INT_LEN),
    (tuple[Union[int, str], ...], INT_LEN + STR_LEN),
]


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
    return f"{_get_origin_string(annotation)}{_get_args_str(annotation)}"


def _get_origin_string(annotation: Any) -> str:
    origin: Any = get_origin(annotation)
    annotation_name: str

    if annotation in [None, type(None)]:
        return "None"
    elif annotation in [..., Ellipsis]:
        return "..."
    elif isinstance(annotation, _SpecialGenericAlias):
        annotation_name = getattr(annotation, "__name__", str(annotation))
    elif isinstance(annotation, type):
        annotation_name = annotation.__name__
    elif origin is not None:
        annotation_name_with_generics: str = str(annotation)
        annotation_name = annotation_name_with_generics.split("[")[0]  # Should never not be a generic here
    else:
        annotation_name = str(annotation)

    annotation_name_without_module: str = _remove_typing_module_from_str(annotation_name)
    if annotation_name_without_module == "Optional":
        return "Union"
    return annotation_name_without_module


def _get_args_str(annotation: Any) -> str:
    args: tuple[Any, ...] = get_args(annotation)
    args_str: str = ", ".join(type_annotation_to_string(arg) for arg in args)

    if len(args) == 0:
        return ""
    return f"[{args_str}]"


def _remove_typing_module_from_str(annotation_str: str) -> str:
    return annotation_str.replace("typing_extensions.", "").replace("typing.", "")
