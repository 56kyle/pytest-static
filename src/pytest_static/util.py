"""Module containing various utility functions used throughout the pytest-static package."""

from typing import Any
from typing import Callable
from typing import get_args
from typing import get_origin

from typing_extensions import _SpecialForm


def get_base_type(typ: Any) -> Any:
    """Returns get_origin if not None, otherwise returns the given type."""
    origin: Any = get_origin(typ)
    if origin is not None:
        return origin
    return typ


def is_subtype(type_a: Any, type_b: Any) -> bool:
    """Returns whether an instance of type_a is always an instance of type_b."""


def is_none_type(typ: Any) -> bool:
    """Returns whether typ is None."""
    return typ is None


def is_class_object(typ: Any) -> bool:
    """Returns whether typ is a class object."""
    return isinstance(typ, type) and typ is not type


def is_generic_alias(typ: Any) -> bool:
    """Returns whether typ is a generic alias."""
    if isinstance(get_origin(typ), type):
        return validate_generic_alias(typ)
    return False


def validate_generic_alias(typ: Any) -> bool:
    """Returns whether typ is a generic alias."""
    args: tuple[Any, ...] = get_args(typ)
    if args:
        return all(is_valid_annotation(arg) for arg in args if isinstance(arg, type))
    return False


def is_special_form(typ: Any) -> bool:
    """Returns whether typ is a special form."""
    return isinstance(typ, _SpecialForm)


__VALID_ANNOTATION_CHECKS: list[Callable[[Any], bool]] = [
    is_none_type,
    is_class_object,
    is_generic_alias,
    is_special_form,
]


def is_valid_annotation(typ: Any) -> bool:
    """Returns whether typ is a valid annotation."""
    return any(check(typ) for check in __VALID_ANNOTATION_CHECKS)
