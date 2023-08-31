from pathlib import Path
from typing import Any
from typing import Iterable
from typing import List
from typing import Sequence

import pytest

from pytest_static.plugin import pytest_configure
from pytest_static.type_sets import BoolParams
from pytest_static.type_sets import BytesParams
from pytest_static.type_sets import ComplexParams
from pytest_static.type_sets import FloatParams
from pytest_static.type_sets import IntParams
from pytest_static.type_sets import StrParams


@pytest.fixture
def conftest(pytester: pytest.Pytester) -> Path:
    return pytester.makeconftest(
        """
        import pytest
        pytest_plugins = ["pytest_static.plugin"]
        """
    )


@pytest.fixture
def argtypes(request: pytest.FixtureRequest) -> Sequence[Any]:
    return getattr(request, "param", ())


@pytest.fixture
def parametrize_types_test(
    pytester: pytest.Pytester, conftest: Path, argtypes: Sequence[str]
) -> Path:
    argnames: List[str] = [f"arg{i}" for i in range(len(argtypes))]
    argtypes_formatted: str = ", ".join([f"{argtype}" for argtype in argtypes])
    signature: str = ", ".join(
        [f"{argname}" for argname, argtype in zip(argnames, argtypes, strict=True)]
    )

    return pytester.makepyfile(
        f"""
        import pytest
        import typing
        from typing import *

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
    pytester: pytest.Pytester, conftest: Path
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
    pytester: pytest.Pytester, conftest: Path
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
    pytester: pytest.Pytester, conftest: Path
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
    ids=lambda x: str(x) if isinstance(x, Iterable) else "",
    indirect=["argtypes"],
)
def test_parametrize_types_with_single_basic(
    pytester: pytest.Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


@pytest.mark.parametrize(
    argnames=["argtypes", "expected"],
    argvalues=[
        (("bool", "int"), len(BoolParams) * len(IntParams)),
    ],
    ids=lambda x: str(x) if isinstance(x, Iterable) else "",
    indirect=["argtypes"],
)
def test_parametrize_types_with_multiple_basic(
    pytester: pytest.Pytester, parametrize_types_test: Path, expected: int
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
    ids=lambda x: str(x) if isinstance(x, Iterable) else "",
    indirect=["argtypes"],
)
def test_parametrize_types_with_single_expanded(
    pytester: pytest.Pytester, parametrize_types_test: Path, expected: int
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
    ids=lambda x: str(x) if isinstance(x, Iterable) else "",
    indirect=["argtypes"],
)
def test_parametrize_types_with_multiple_expanded(
    pytester: pytest.Pytester, parametrize_types_test: Path, expected: int
) -> None:
    result: pytest.RunResult = pytester.runpytest(parametrize_types_test)
    result.assert_outcomes(passed=expected)


def test_pytest_configure(pytester: pytest.Pytester) -> None:
    config: pytest.Config = pytester.parseconfig()
    assert len(config.getini("markers")) == 0
    pytest_configure(config)
    assert "parametrize_types" in config.getini("markers")[0]
