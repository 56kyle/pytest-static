"""The pytest-static pytest plugin."""

import pytest
from _pytest.python import Metafunc

from pytest_static.parametric import parametrize_types


def pytest_generate_tests(metafunc: Metafunc) -> None:
    """Generate parametrized tests for the given argnames and types."""
    for marker in metafunc.definition.iter_markers(name="parametrize_types"):
        parametrize_types(metafunc, *marker.args, **marker.kwargs)


def pytest_configure(config: pytest.Config) -> None:
    """Adds pytest-static plugin markers to the pytest CLI."""
    config.addinivalue_line(
        "markers",
        "parametrize_types(argnames, argtypes, ids, *type_args, **kwargs):"
        " Generate parametrized tests for the given argnames and types in argtypes.",
    )
