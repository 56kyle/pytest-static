from dataclasses import dataclass
from typing import Any
from typing import Generator

import pytest

from pytest_static.custom_typing import TypeHandler
from pytest_static.type_handler import TypeHandlerRegistry


class TestTypeHandlerRegistry:
    def test___getitem___with_unregistered(self, type_handler_registry: TypeHandlerRegistry) -> None:
        with pytest.raises(KeyError):
            assert type_handler_registry[int]

    def test___getitem___with_basic(
        self,
        type_handler_registry__basic: TypeHandlerRegistry,
        basic_handler: TypeHandler
    ) -> None:
        assert type_handler_registry__basic[int] == [basic_handler]

    def test_get_with_unregistered(self, type_handler_registry: TypeHandlerRegistry) -> None:
        assert type_handler_registry.get(int, None) is None

    def test_get_with_basic(
        self,
        type_handler_registry__basic: TypeHandlerRegistry,
        basic_handler: TypeHandler
    ) -> None:
        assert type_handler_registry__basic.get(int, None) == [basic_handler]

    def test_register_with_unregistered(self, type_handler_registry: TypeHandlerRegistry) -> None:
        assert type_handler_registry.get(int, None) is None

    def test_register_with_basic(
        self,
        type_handler_registry: TypeHandlerRegistry,
        basic_handler: TypeHandler
    ) -> None:
        type_handler_registry.register(int)(basic_handler)
        assert type_handler_registry.get(int, None) is not None
        assert tuple(type_handler_registry.get(int, None)[0](int, ())) == (1, 2, 3)

    def test_register_with_existing(
        self,
        type_handler_registry__basic: TypeHandlerRegistry,
        basic_handler: TypeHandler
    ) -> None:
        type_handler_registry__basic.register(int)(basic_handler)
        assert type_handler_registry__basic.get(int, None) is not None
        assert tuple(type_handler_registry__basic.get(int, None)[0](int, ())) == (1, 2, 3)

    def test_clear_with_unregistered(self, type_handler_registry: TypeHandlerRegistry) -> None:
        assert type_handler_registry.get(int, None) is None
        type_handler_registry.clear(int)
        assert type_handler_registry.get(int, None) is None

    def test_clear_with_basic(
        self,
        type_handler_registry__basic: TypeHandlerRegistry,
        basic_handler: TypeHandler
    ) -> None:
        assert type_handler_registry__basic.get(int, None) == [basic_handler]
        assert tuple(type_handler_registry__basic.get(int, None)[0](int, ())) == (1, 2, 3)

        type_handler_registry__basic.clear(int)
        assert type_handler_registry__basic.get(int, None) == []
