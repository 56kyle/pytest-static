"""Module containing custom types used throughout pytest-static."""

from typing import Any
from typing import Callable
from typing import Generator
from typing import TypeVar
from typing import Union

from typing_extensions import Literal
from typing_extensions import ParamSpec


__all__: list[str] = [
    "_UnionGenericAlias",
    "_LiteralSpecialForm",
    "_ScopeName",
    "T",
    "KT",
    "VT",
    "T_co",
    "P",
    "TypeHandler",
]


_UnionGenericAlias = type(Union)
_LiteralSpecialForm = type(Literal)


# Redefines pytest's typing for 100% test coverage
_ScopeName = Literal["session", "package", "module", "class", "function"]


T = TypeVar("T")
KT = TypeVar("KT")
VT = TypeVar("VT")

T_co = TypeVar("T_co", covariant=True)

P = ParamSpec("P")


class Missing:
    """Custom missing class used for a lack of a passed value that counts None as a value."""


MISSING: Missing = Missing()


TypeHandler = Callable[[Any, tuple[Any, ...]], Generator[Any, None, None]]
