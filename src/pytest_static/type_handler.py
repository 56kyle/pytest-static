"""Module containing the TypeHandlerRegistry class for providing semi-read only Mappings with selective registration."""

from __future__ import annotations

import types
from dataclasses import MISSING
from typing import Any
from typing import Callable
from typing import Generator
from typing import Generic
from typing import Iterable

from typing_extensions import get_args

from pytest_static.custom_typing import KT
from pytest_static.custom_typing import VT
from pytest_static.custom_typing import TypeHandler
from pytest_static.util import get_base_type


class TypeHandlerRegistry(Generic[KT, VT]):
    """Registry for various TypeHandler callbacks."""

    def __init__(self, *args: Any, **kwargs: Any):
        """Sets up the Registry."""
        self._mapping: dict[KT, VT] = {}
        self._proxy: types.MappingProxyType = types.MappingProxyType(self._mapping)

    def __getitem__(self, __key: KT) -> VT:
        """Returns from proxy."""
        return self._proxy.__getitem__(__key)

    def register(self, *args: KT) -> Callable[[TypeHandler], TypeHandler]:
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

        def decorator(fn: TypeHandler) -> TypeHandler:
            for key in args:
                base_type: Any = get_base_type(key)
                if self._proxy.get(base_type, MISSING) is MISSING:
                    self._mapping[base_type] = []
                self._mapping[base_type].append(fn)
                return fn

        return decorator

    def get_instances(self, key: KT) -> tuple[VT, ...]:
        """Returns a tuple of instances KT retrieved from the registered callbacks."""
        return tuple(*self.iter_instances(key))

    def iter_instances(self, key: KT) -> Generator[VT, None, None]:
        """Returns a Generator that yields from all handlers."""
        base_type: Any = get_base_type(key)
        type_args: tuple[Any, ...] = get_args(key)

        handlers: Iterable[TypeHandler] = self._proxy.get(base_type, None)
        if handlers is None:
            raise KeyError(f"Failed to find a handler for {key=}.")
        for handler in handlers:
            yield from handler(base_type, type_args)
