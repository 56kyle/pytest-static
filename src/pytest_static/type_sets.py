"""Default type sets for pytest_static to use in parametrization."""
from typing import Any
from typing import Dict
from typing import Set
from typing import TypeVar


T = TypeVar("T", bound=Any)


BoolParams: Set[bool] = {True, False}

IntParams: Set[int] = {
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

Whitespace: Set[str] = {" ", "\t", "\n", "\r", "\v", "\f"}
SpecialChars: Set[str] = {
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
Digits: Set[str] = {"0", "1", "2", "3", "4", "5", "6", "7", "8", "9"}
LowercaseLetters: Set[str] = {
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
}
UppercaseLetters: Set[str] = {
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
    "G",
    "H",
    "I",
    "J",
    "K",
    "L",
    "M",
    "N",
    "O",
    "P",
    "Q",
    "R",
    "S",
    "T",
    "U",
    "V",
    "W",
    "X",
    "Y",
    "Z",
}
UnicodeChars: Set[str] = {
    "\u00E9",
    "\u00F1",
    "\u2603",
    "\u00A9",
    "\u00AE",
    "\U0001F600",
}
ForeignChars: Set[str] = {"Д", "д", "ב", "ע", "α", "Ω", "い", "ろ", "は", "我", "们"}
EscapeSequences: Set[str] = {
    "\\\\",
    "\\'",
    '\\"',
    "\\n",
    "\\r",
    "\\t",
    "\\x00",
    "\\x7F",
}
TripleQuotes: Set[str] = {'"""', "'''"}

StrParams: Set[str] = {
    "",
    *Whitespace,
    *SpecialChars,
    *Digits,
    *LowercaseLetters,
    *UppercaseLetters,
    *UnicodeChars,
    *ForeignChars,
    *EscapeSequences,
    *TripleQuotes,
}

FloatParams: Set[float] = {
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

ComplexParams: Set[complex] = {
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

BytesParams: Set[bytes] = {
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
    bool: BoolParams,
    int: IntParams,
    float: FloatParams,
    complex: ComplexParams,
    str: StrParams,
    bytes: BytesParams,
    type(None): {None},
    ...: set(),
    Ellipsis: set(),
}
