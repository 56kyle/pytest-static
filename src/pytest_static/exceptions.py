"""Custom exception classes used in pytest-static."""
from typing import Any


class ExpandedTypeNotCallableError(TypeError):
    """Exception raised if a non-Callable base_type is being cast as Callable."""

    def __init__(self, base_type: Any, *args: Any):
        msg: str = (
            f"Attempted to cast a non callable type of {type(base_type)} "
            f"as callable."
        )
        super().__init__(msg, *args)
