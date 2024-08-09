"""Fixtures used in unit tests."""

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_static.type_handler import TypeHandlerRegistry


@pytest.fixture(scope="function")
def type_handler_registry(request: FixtureRequest) -> TypeHandlerRegistry:
    return getattr(request, "param", TypeHandlerRegistry())
