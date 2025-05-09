"""Module containing the TypeHandlerRegistry class for providing semi-read only Mappings with selective registration."""

from __future__ import annotations

import types
from dataclasses import MISSING
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import get_args

from pytest_static.util import get_base_type


if TYPE_CHECKING:
    from pytest_static.custom_typing import TypeHandler


class TypeHandlerRegistry:
    """Registry for various TypeHandler callbacks."""

    def __init__(self) -> None:
        """Sets up the Registry."""
        self._mapping: dict[Any, list[TypeHandler]] = {}
        self._proxy: types.MappingProxyType[Any, list[TypeHandler]] = types.MappingProxyType(self._mapping)

    @classmethod
    def _validate_has_no_generic(cls, typ: Any) -> None:
        """Validates that the provided typ has no generic type."""
        if get_args(typ):
            raise TypeError(f"Cannot register a type handler type containing generics: {typ}")

    def __getitem__(self, key: Any) -> Any:
        """Returns from proxy."""
        return self._proxy.__getitem__(key)

    def get(self, key: Any, default: Any = None, /) -> Any:
        """Returns from proxy."""
        return self._proxy.get(key, default)

    def register(self, *args: Any) -> Callable[[TypeHandler], TypeHandler]:
        """Returns a decorator that registers a Callback to each of the provided keys.

        Usage:
            @type_handlers.register(int)
            def my_function_name(base_type, type_args):
                yield from [100, 1000]

            @type_handlers.register(int, float)
            def my_function_name(base_type, type_args):
                for i in range(5):
                    yield base_type(i)

            type_handlers.get_instances(int) => (100, 1000, 1, 2, 3, 4, 5)
            type_handlers.get_instances(float) => (1.0, 2.0, 3.0, 4.0, 5.0)
        """
        for arg in args:
            self._validate_has_no_generic(arg)

        def decorator(fn: TypeHandler) -> TypeHandler:
            for key in args:
                base_type: Any = get_base_type(key)
                if self._proxy.get(base_type, MISSING) == MISSING:
                    self._mapping[base_type] = []
                self._mapping[base_type].append(fn)
            return fn

        return decorator

    def clear(self, typ: Any) -> None:
        """Clears all handlers from the provided typ."""
        if self._mapping.get(typ, None) is not None:
            self._mapping[typ] = []
