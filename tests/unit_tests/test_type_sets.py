from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS
from pytest_static.type_sets import BoolParams
from pytest_static.type_sets import BytesParams
from pytest_static.type_sets import ComplexParams
from pytest_static.type_sets import Digits
from pytest_static.type_sets import EscapeSequences
from pytest_static.type_sets import FloatParams
from pytest_static.type_sets import ForeignChars
from pytest_static.type_sets import IntParams
from pytest_static.type_sets import LowercaseLetters
from pytest_static.type_sets import SpecialChars
from pytest_static.type_sets import StrParams
from pytest_static.type_sets import TripleQuotes
from pytest_static.type_sets import UnicodeChars
from pytest_static.type_sets import UppercaseLetters
from pytest_static.type_sets import Whitespace


def test_type_sets() -> None:
    assert PREDEFINED_INSTANCE_SETS
    for type_set in PREDEFINED_INSTANCE_SETS.values():
        assert type_set is not None


def test_bool_params() -> None:
    assert BoolParams


def test_int_params() -> None:
    assert IntParams


def test_whitespace() -> None:
    assert Whitespace


def test_special_chars() -> None:
    assert SpecialChars


def test_digits() -> None:
    assert Digits


def test_lowercase_letters() -> None:
    assert LowercaseLetters


def test_uppercase_letters() -> None:
    assert UppercaseLetters


def test_unicode_chars() -> None:
    assert UnicodeChars


def test_foreign_chars() -> None:
    assert ForeignChars


def test_escape_sequences() -> None:
    assert EscapeSequences


def test_triple_quotes() -> None:
    assert TripleQuotes


def test_str_params() -> None:
    assert StrParams


def test_float_params() -> None:
    assert FloatParams


def test_complex_params() -> None:
    assert ComplexParams


def test_bytes_params() -> None:
    assert BytesParams
