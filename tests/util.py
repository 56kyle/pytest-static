"""Common utility functions and info for pytest-static tests."""
from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Literal
from typing import Optional
from typing import Set
from typing import Tuple
from typing import Union
from typing import _GenericAlias
from typing import get_args

from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS


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


PRODUCT_TYPE_SINGLE_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (List[int], INT_LEN),
    (list[int], INT_LEN),
    (Set[int], INT_LEN),
    (set[int], INT_LEN),
    (FrozenSet[int], INT_LEN),
    (frozenset[int], INT_LEN),
]


PRODUCT_TYPE_DOUBLE_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Dict[bool, int], BOOL_LEN * INT_LEN),
    (dict[bool, int], BOOL_LEN * INT_LEN),
    (Dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),
    (dict[bool, Union[int, str]], BOOL_LEN * (INT_LEN + STR_LEN)),
]


PRODUCT_TYPE_SEVERAL_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),
    (tuple[bool, int, str], BOOL_LEN * INT_LEN * STR_LEN),
    (
        Tuple[Union[bool, int], int, Union[bool, str]],
        (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN),
    ),
    (
        tuple[Union[bool, int], int, Union[bool, str]],
        (BOOL_LEN + INT_LEN) * INT_LEN * (BOOL_LEN + STR_LEN),
    ),
]


PRODUCT_TYPE_PARAM_SPEC_GENERIC_EXPECTED_EXAMPLES: list[tuple[Any, int]] = [
    (Tuple[int, ...], INT_LEN),
    (tuple[int, ...], INT_LEN),
    (Tuple[Union[int, str], ...], INT_LEN + STR_LEN),
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
    if annotation in [None, type(None)]:
        return "None"
    elif isinstance(annotation, type):
        # It's a built-in type
        args: tuple[Any, ...] = get_args(annotation)
        if len(args) == 0:
            return annotation.__name__
        args_str: str = ", ".join(type_annotation_to_string(arg) for arg in args)
        return annotation.__name__ + f"[{args_str}]"
    elif isinstance(annotation, _GenericAlias):
        # It's a complex type from the typing module
        args: tuple[Any, ...] = get_args(annotation)
        if len(args) == 0:
            return annotation.__name__
        args_str: str = ", ".join(type_annotation_to_string(arg) for arg in args)
        name: str = (
            annotation.__name__ if annotation.__name__ != "Optional" else "Union"
        )
        return name + f"[{args_str}]"
    else:
        # Fallback for other types
        return str(annotation)
