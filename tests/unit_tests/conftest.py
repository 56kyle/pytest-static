from typing import Any
from typing import List
from typing import Tuple

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_static.parametric import ExpandedType
from pytest_static.parametric import T_co


@pytest.fixture(scope="function")
def expanded_type(
    request: FixtureRequest,
    base_type: T_co,
    type_arguments: Tuple[Any, ...],
) -> ExpandedType[T_co]:
    return getattr(
        request,
        "param",
        ExpandedType(
            base_type=base_type,
            type_arguments=type_arguments,
        ),
    )


@pytest.fixture(scope="function")
def base_type(request: FixtureRequest) -> Any:
    return getattr(request, "param", List)


@pytest.fixture(scope="function")
def type_arguments(
    request: FixtureRequest,
) -> Tuple[Any, ...]:
    return getattr(request, "param", (int,))
