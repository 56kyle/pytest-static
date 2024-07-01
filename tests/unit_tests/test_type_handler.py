from typing import Any
from typing import Generator

from pytest_static.type_handler import TypeHandlerRegistry


class TestTypeHandlerRegistry:
    def test_register(self, type_handler_registry: TypeHandlerRegistry) -> None:
        assert type_handler_registry.get(int, None) is None

        @type_handler_registry.register(int)
        def _iter_int(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
            yield from (1, 2, 3)

        assert type_handler_registry.get(int, None) is not None
        assert tuple(type_handler_registry.get(int, None)[0](int, ())) == (1, 2, 3)

    def test_clear(self, type_handler_registry: TypeHandlerRegistry) -> None:
        @type_handler_registry.register(int)
        def _iter_int(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
            yield from (1, 2, 3)

        assert type_handler_registry.get(int, None) is not None
        assert tuple(type_handler_registry.get(int, None)[0](int, ())) == (1, 2, 3)

        type_handler_registry.clear(int)
        assert type_handler_registry.get(int, None) == []
