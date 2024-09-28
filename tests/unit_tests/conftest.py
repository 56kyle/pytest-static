"""Fixtures used in unit tests."""
from typing import Any
from typing import Generator

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_static.custom_typing import TypeHandler
from pytest_static.type_handler import TypeHandlerRegistry




@pytest.fixture(scope="function")
def type_handler_registry(request: FixtureRequest) -> TypeHandlerRegistry:
    return getattr(request, "param", TypeHandlerRegistry())


@pytest.fixture(scope="function")
def type_handler_registry__basic(
    request: FixtureRequest,
    type_handler_registry: TypeHandlerRegistry,
    basic_type: Any,
    basic_handler: TypeHandler
) -> TypeHandlerRegistry:
    type_handler_registry.register(int)(basic_handler)
    return getattr(request, 'param', type_handler_registry)


@pytest.fixture(scope="function")
def basic_type(request: FixtureRequest) -> Any:
    return getattr(request, 'param', int)


@pytest.fixture(scope="function")
def basic_handler(request: FixtureRequest) -> TypeHandler:
    def _iter_int(base_type: Any, type_args: tuple[Any, ...]) -> Generator[Any, None, None]:
        yield from (1, 2, 3)
    return getattr(request, 'param', _iter_int)





