"""Default type sets for pytest_static to use in parametrization."""

import string
from collections.abc import Mapping
from types import MappingProxyType
from typing import Any
from typing import TypeVar


T = TypeVar("T", bound=Any)


BOOL_PARAMS: frozenset[bool] = frozenset({True, False})

INT_PARAMS: frozenset[int] = frozenset(
    {
        0,
        1,
        -1,
        2,
        -2,
        2147483647,
        -2147483648,
        9223372036854775807,
        -9223372036854775808,
    }
)

WHITESPACE: frozenset[str] = frozenset(string.whitespace)
PUNCTUATION: frozenset[str] = frozenset(string.punctuation)
DIGITS: frozenset[str] = frozenset(string.digits)
LOWERCASE_LETTERS: frozenset[str] = frozenset(string.ascii_lowercase)
UPPERCASE_LETTERS: frozenset[str] = frozenset(string.ascii_uppercase)
UNICODE_CHARS: frozenset[str] = frozenset(
    {
        "\u00e9",
        "\u00f1",
        "\u2603",
        "\u00a9",
        "\u00ae",
        "\U0001f600",
    }
)
FOREIGN_CHARS: frozenset[str] = frozenset({"Д", "д", "ב", "ע", "α", "Ω", "い", "ろ", "は", "我", "们"})  # noqa: RUF001
ESCAPE_SEQUENCES: frozenset[str] = frozenset(
    {
        "\\\\",
        "\\'",
        '\\"',
        "\\n",
        "\\r",
        "\\t",
        "\\x00",
        "\\x7F",
    }
)
TRIPLE_QUOTES: frozenset[str] = frozenset({'"""', "'''"})

STR_PARAMS: frozenset[str] = frozenset(
    {
        "",
        *WHITESPACE,
        *PUNCTUATION,
        *DIGITS,
        *LOWERCASE_LETTERS,
        *UPPERCASE_LETTERS,
        *UNICODE_CHARS,
        *FOREIGN_CHARS,
        *ESCAPE_SEQUENCES,
        *TRIPLE_QUOTES,
    }
)

FLOAT_PARAMS: frozenset[float] = frozenset(
    {
        0.0,
        -0.0,
        1.0,
        -1.0,
        1e-10,
        -1e-10,
        1e10,
        -1e10,
        float("inf"),
        -float("inf"),
        float("nan"),
    }
)

COMPLEX_PARAMS: frozenset[complex] = frozenset(
    {
        0j,
        1j,
        -1j,
        1 + 1j,
        -1 - 1j,
        1e-10j,
        -1e-10j,
        1e10j,
        -1e10j,
        (1e-10 + 1e-10j),
        (-1e-10 - 1e-10j),
        (1e10 + 1e10j),
        (-1e10 - 1e10j),
    }
)

BYTES_PARAMS: frozenset[bytes] = frozenset(
    {
        b"",
        b"\x00",
        b"\xff",
        b"\x00\xff",
        b"\xff\x00",
        b" ",
        b"\t",
        b"\n",
        b"\r",
        b"\v",
        b"\f",
        b"0",
        b"1",
        b"2",
        b"3",
        b"4",
        b"5",
        b"6",
        b"7",
        b"8",
        b"9",
        b"a",
        b"A",
        b"z",
        b"Z",
        b"\x80",
        b"\xfe",
    }
)


_default_instance_sets: dict[Any, set[Any]] = {
    bool: set(BOOL_PARAMS),
    int: set(INT_PARAMS),
    float: set(FLOAT_PARAMS),
    complex: set(COMPLEX_PARAMS),
    str: set(STR_PARAMS),
    bytes: set(BYTES_PARAMS),
    type(None): {None},
}

DEFAULT_INSTANCE_SETS: Mapping[Any, set[Any]] = MappingProxyType(_default_instance_sets)
