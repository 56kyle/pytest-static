"""Default type sets for pytest_static to use in parametrization."""

import string
from typing import Any
from typing import Dict
from typing import Set
from typing import TypeVar


T = TypeVar("T", bound=Any)


BOOL_PARAMS: Set[bool] = {True, False}

INT_PARAMS: Set[int] = {
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

WHITESPACE: Set[str] = {" ", "\t", "\n", "\r", "\v", "\f"}
SPECIAL_CHARS: Set[str] = {
    "!",
    "@",
    "#",
    "$",
    "%",
    "^",
    "&",
    "*",
    "(",
    ")",
    "-",
    "+",
    "=",
    "{",
    "}",
    "[",
    "]",
    "|",
    "\\",
    ";",
    ":",
    "'",
    '"',
    ",",
    "<",
    ".",
    ">",
    "/",
    "?",
    "`",
    "~",
}
DIGITS: Set[str] = set(string.digits)
LOWERCASE_LETTERS: Set[str] = set(string.ascii_lowercase)
UPPERCASE_LETTERS: Set[str] = set(string.ascii_uppercase)
UNICODE_CHARS: Set[str] = {
    "\u00E9",
    "\u00F1",
    "\u2603",
    "\u00A9",
    "\u00AE",
    "\U0001F600",
}
FOREIGN_CHARS: Set[str] = {"Д", "д", "ב", "ע", "α", "Ω", "い", "ろ", "は", "我", "们"}
ESCAPE_SEQUENCES: Set[str] = {
    "\\\\",
    "\\'",
    '\\"',
    "\\n",
    "\\r",
    "\\t",
    "\\x00",
    "\\x7F",
}
TRIPLE_QUOTES: Set[str] = {'"""', "'''"}

STR_PARAMS: Set[str] = {
    "",
    *WHITESPACE,
    *SPECIAL_CHARS,
    *DIGITS,
    *LOWERCASE_LETTERS,
    *UPPERCASE_LETTERS,
    *UNICODE_CHARS,
    *FOREIGN_CHARS,
    *ESCAPE_SEQUENCES,
    *TRIPLE_QUOTES,
}

FLOAT_PARAMS: Set[float] = {
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

COMPLEX_PARAMS: Set[complex] = {
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

BYTES_PARAMS: Set[bytes] = {
    b"",
    b"\x00",
    b"\xFF",
    b"\x00\xFF",
    b"\xFF\x00",
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
    b"\xFE",
}


PREDEFINED_INSTANCE_SETS: Dict[Any, Set[Any]] = {
    bool: BOOL_PARAMS,
    int: INT_PARAMS,
    float: FLOAT_PARAMS,
    complex: COMPLEX_PARAMS,
    str: STR_PARAMS,
    bytes: BYTES_PARAMS,
    type(None): {None},
    ...: set(),
    Ellipsis: set(),
}
