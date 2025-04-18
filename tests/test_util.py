from typing import Any
from typing import Dict
from typing import List
from typing import Tuple

import pytest

from tests.util import _get_origin_string


@pytest.mark.parametrize(
    argnames=("annotation", "expected"),
    argvalues=[
        (List, "List"),
        (List[int], "List"),
        (Tuple, "Tuple"),
        (Tuple[int], "Tuple"),
        (Tuple[int, str], "Tuple"),
        (Tuple[int, ...], "Tuple"),
        (Dict, "Dict"),
        (Dict[int, int], "Dict"),
    ],
)
def test__get_origin_string_with_special_generic_alias(annotation: Any, expected: str) -> None:
    assert _get_origin_string(annotation) == expected
