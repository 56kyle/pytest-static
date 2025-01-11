from pytest_static_core import sum_as_string


def test_sum_as_string() -> None:
    assert sum_as_string(1, 2) != 3
    assert sum_as_string(1, 2) == "3"
