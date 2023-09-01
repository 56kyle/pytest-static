from typing import Any
from typing import List
from typing import Tuple
from typing import Type
from typing import Union

import pytest
from _pytest.fixtures import FixtureRequest

from pytest_static.parametric import ExpandedType
from pytest_static.parametric import T


@pytest.fixture(scope="function")
def expanded_type(
    request: FixtureRequest,
    primary_type: Type[T],
    type_args: Tuple[Union[Any, ExpandedType[Any]], ...],
) -> ExpandedType[T]:
    return getattr(
        request,
        "param",
        ExpandedType(
            primary_type=primary_type,
            type_args=type_args,
        ),
    )


@pytest.fixture(scope="function")
def primary_type(request: FixtureRequest) -> Type[Any]:
    return getattr(request, "param", List)


@pytest.fixture(scope="function")
def type_args(request: FixtureRequest) -> Tuple[Union[Any, ExpandedType[Any]], ...]:
    return getattr(request, "param", (int,))
