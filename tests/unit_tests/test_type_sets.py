from src.pytest_static.type_sets import PREDEFINED_TYPE_SETS


def test_type_sets() -> None:
    assert PREDEFINED_TYPE_SETS
    for type_set in PREDEFINED_TYPE_SETS.values():
        assert type_set
