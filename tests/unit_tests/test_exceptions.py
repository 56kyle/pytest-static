import pytest

from pytest_static.exceptions import ExpandedTypeNotCallableError


def test_expanded_type_not_callable_error() -> None:
    with pytest.raises(TypeError) as e:
        raise ExpandedTypeNotCallableError(int)
    e.match(r".*<class 'type'>.*")
