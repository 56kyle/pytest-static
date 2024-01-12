from pathlib import Path
from typing import Iterable
from typing import List
from typing import Sequence

import pytest
from _pytest.fixtures import FixtureRequest
from _pytest.pytester import Pytester

from pytest_static.plugin import pytest_configure
from pytest_static.type_sets import BoolParams
from pytest_static.type_sets import BytesParams
from pytest_static.type_sets import ComplexParams
from pytest_static.type_sets import FloatParams
from pytest_static.type_sets import IntParams
from pytest_static.type_sets import StrParams
from tests.util import BASIC_TYPE_EXPECTED_EXAMPLES
from tests.util import PRODUCT_TYPE_EXPECTED_EXAMPLES
from tests.util import SPECIAL_TYPE_EXPECTED_EXAMPLES
from tests.util import SUM_TYPE_EXPECTED_EXAMPLES
from tests.util import type_annotation_to_string


@pytest.fixture
def conftest(pytester: Pytester) -> Path:
    return pytester.makeconftest(
        """
        import pytest
        pytest_plugins = ["pytest_static.plugin"]
        """
    )


@pytest.fixture
def argtypes(request: FixtureRequest) -> Sequence[str]:
    return getattr(request, "param", [])


@pytest.fixture
def parametrize_types_test(
    pytester: Pytester, conftest: Path, argtypes: Sequence[str]
) -> Path:
    argnames: List[str] = [f"arg{i}" for i in range(len(argtypes))]
    argtypes_formatted: str = ", ".join([f"{argtype}" for argtype in argtypes])
    signature: str = ", ".join(
        [f"{argname}" for argname, argtype in zip(argnames, argtypes)]
    )

    return pytester.makepyfile(
        f"""
        import pytest
        import typing
        from typing import *
        from typing_extensions import Literal, ParamSpec, get_origin, get_args

        @pytest.mark.parametrize_types(
            argnames={argnames},
            argtypes=[{argtypes_formatted}],
            ids=lambda x: str(x)
        )
        def test_func({signature}) -> None:
            pass
        """
    )


def test_parametrize_types_with_unequal_names_and_types(
    pytester: Pytester, conftest: Path
) -> None:
    test_path: Path = pytester.makepyfile(
        """
        import pytest
        import typing
        from typing import *

        @pytest.mark.parametrize_types(
            argnames=["a", "b"],
            argtypes=[int, float, str],
        )
        def test_func(a, b) -> None:
            assert a
            assert b
        """
    )
    result: pytest.RunResult = pytester.runpytest(test_path)
    result.assert_outcomes(errors=1)


def test_parametrize_types_with_no_ids_provided(
    pytester: Pytester, conftest: Path
) -> None:
    test_path: Path = pytester.makepyfile(
        """
        import pytest
        import typing
        from typing import *

        @pytest.mark.parametrize_types(
            argnames=["a", "b"],
            argtypes=[bool, bool],
        )
        def test_func(a, b) -> None:
            assert a is not None
            assert b is not None
        """
    )
    result: pytest.RunResult = pytester.runpytest(test_path)
    result.assert_outcomes(passed=4)


def test_parametrize_types_with_argnames_as_string(
    pytester: Pytester, conftest: Path
) -> None:
    test_path: Path = pytester.makepyfile(
        """
        import pytest
        import typing
        from typing import *

        @pytest.mark.parametrize_types(
            argnames="a, b",
            argtypes=[bool, bool],
        )
        def test_func(a, b) -> None:
            assert a is not None
            assert b is not None
        """
    )
    result: pytest.RunResult = pytester.runpytest(test_path)
    result.assert_outcomes(passed=4)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        (("bool",), len(BoolParams)),
        (("int",), len(IntParams)),
        (("float",), len(FloatParams)),
        (("complex",), len(ComplexParams)),
        (("str",), len(StrParams)),
        (("bytes",), len(BytesParams)),
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_single_basic(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        (("bool", "int"), len(BoolParams) * len(IntParams)),
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_multiple_basic(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        (("List[int]",), len(IntParams)),
        (("List[str]",), len(StrParams)),
        (("Dict[bool, int]",), len(BoolParams) * len(IntParams)),
        (("Dict[str, bool]",), len(StrParams) * len(BoolParams)),
        (("Tuple[int, str]",), len(IntParams) * len(StrParams)),
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_single_expanded(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        (("List[int]", "List[str]"), len(IntParams) * len(StrParams)),
        (
            ("List[int]", "Dict[bool, int]"),
            len(IntParams) * len(BoolParams) * len(IntParams),
        ),
        (
            ("List[int]", "Dict[str, bool]"),
            len(IntParams) * len(StrParams) * len(BoolParams),
        ),
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_multiple_expanded(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        ((type_annotation_to_string(typ),), expected)
        for typ, expected in SPECIAL_TYPE_EXPECTED_EXAMPLES
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_special_type_expected_examples(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        ((type_annotation_to_string(typ),), expected)
        for typ, expected in BASIC_TYPE_EXPECTED_EXAMPLES
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_basic_type_expected_examples(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        ((type_annotation_to_string(typ),), expected)
        for typ, expected in SUM_TYPE_EXPECTED_EXAMPLES
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_sum_type_expected_examples(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        ((type_annotation_to_string(typ),), expected)
        for typ, expected in PRODUCT_TYPE_EXPECTED_EXAMPLES
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else x,
    indirect=["argtypes"],
)
def test_parametrize_types_with_product_type_expected_examples(
    pytester: Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


def test_pytest_configure(pytester: Pytester) -> None:
    config: pytest.Config = pytester.parseconfig()
    assert len(config.getini("markers")) == 0
    pytest_configure(config)
    assert "parametrize_types" in config.getini("markers")[0]
