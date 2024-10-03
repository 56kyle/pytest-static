"""Module containing various utility functions used throughout the pytest-static package."""

from typing import Any
from typing import get_origin


def get_base_type(typ: Any) -> Any:
    """Returns get_origin if not None, otherwise returns the given type."""
    origin: Any = get_origin(typ)
    if origin is not None:
        return origin
    return typ
