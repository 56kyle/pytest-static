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
    base_type: Type[T],
    type_arguments: Tuple[Union[Any, ExpandedType[Any]], ...],
) -> ExpandedType[T]:
    return getattr(
        request,
        "param",
        ExpandedType(
            base_type=base_type,
            type_arguments=type_arguments,
        ),
    )


@pytest.fixture(scope="function")
def base_type(request: FixtureRequest) -> Type[Any]:
    return getattr(request, "param", List)


@pytest.fixture(scope="function")
def type_arguments(
    request: FixtureRequest,
) -> Tuple[Union[Any, ExpandedType[Any]], ...]:
    return getattr(request, "param", (int,))
