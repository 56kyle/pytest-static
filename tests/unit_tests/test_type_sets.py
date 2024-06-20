from pytest_static.type_sets import BOOL_PARAMS
from pytest_static.type_sets import BYTES_PARAMS
from pytest_static.type_sets import COMPLEX_PARAMS
from pytest_static.type_sets import DIGITS
from pytest_static.type_sets import ESCAPE_SEQUENCES
from pytest_static.type_sets import FLOAT_PARAMS
from pytest_static.type_sets import FOREIGN_CHARS
from pytest_static.type_sets import INT_PARAMS
from pytest_static.type_sets import LOWERCASE_LETTERS
from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS
from pytest_static.type_sets import PUNCTUATION
from pytest_static.type_sets import STR_PARAMS
from pytest_static.type_sets import TRIPLE_QUOTES
from pytest_static.type_sets import UNICODE_CHARS
from pytest_static.type_sets import UPPERCASE_LETTERS
from pytest_static.type_sets import WHITESPACE


def test_type_sets() -> None:
    assert PREDEFINED_INSTANCE_SETS
    for type_set in PREDEFINED_INSTANCE_SETS.values():
        assert type_set is not None


def test_bool_params() -> None:
    assert BOOL_PARAMS


def test_int_params() -> None:
    assert INT_PARAMS


def test_whitespace() -> None:
    assert WHITESPACE


def test_special_chars() -> None:
    assert PUNCTUATION


def test_digits() -> None:
    assert DIGITS


def test_lowercase_letters() -> None:
    assert LOWERCASE_LETTERS


def test_uppercase_letters() -> None:
    assert UPPERCASE_LETTERS


def test_unicode_chars() -> None:
    assert UNICODE_CHARS


def test_foreign_chars() -> None:
    assert FOREIGN_CHARS


def test_escape_sequences() -> None:
    assert ESCAPE_SEQUENCES


def test_triple_quotes() -> None:
    assert TRIPLE_QUOTES


def test_str_params() -> None:
    assert STR_PARAMS


def test_float_params() -> None:
    assert FLOAT_PARAMS


def test_complex_params() -> None:
    assert COMPLEX_PARAMS


def test_bytes_params() -> None:
    assert BYTES_PARAMS
