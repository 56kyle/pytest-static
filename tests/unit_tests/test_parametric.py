from __future__ import annotations

from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import TypeVar
from typing import Union

import pytest
from _pytest.monkeypatch import MonkeyPatch
from typing_extensions import Literal

from pytest_static import type_sets
from pytest_static.parametric import ExpandedType
from pytest_static.parametric import T_co
from pytest_static.parametric import expand_type
from pytest_static.type_sets import PREDEFINED_INSTANCE_SETS


NoneType: type[None] = type(None)


T = TypeVar("T", bound=Any)


class DummyClassNoArgs:
    pass


class TestExpandedType:
    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments"],
        argvalues=[(int, tuple()), (float, tuple())],
        indirect=True,
    )
    def test_get_instances_with_basic(self, expanded_type: ExpandedType[T]) -> None:
        assert expanded_type.get_instances() == tuple(
            PREDEFINED_INSTANCE_SETS[expanded_type.base_type]
        )

    def test_get_instances_with_basic_covariant(self) -> None:
        expanded_type: ExpandedType[list[int]] = ExpandedType(list, (int,))
        assert expanded_type.get_instances() == tuple(
            [value] for value in PREDEFINED_INSTANCE_SETS[int]
        )

    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments"],
        argvalues=[
            (
                Literal,
                (1, 2, 3),
            ),
            (
                Literal,
                (Literal[1, 2], 3),
            ),
            (
                Literal,
                (Literal[1, 2], Literal[2, 3]),
            ),
        ],
        ids=["basic", "nested_literal", "overlapping_nested_literal"],
        indirect=True,
    )
    def test_get_instances_with_literal(
        self, expanded_type: ExpandedType[Literal]
    ) -> None:
        assert expanded_type.get_instances() == (1, 2, 3)

    def test_get_instances_with_nested(self) -> None:
        expanded_type = ExpandedType(list, (ExpandedType(list, (int,)),))
        assert expanded_type.get_instances() == tuple(
            [value] for value in PREDEFINED_INSTANCE_SETS[int]
        )

    def test_get_instances_with_multiple(self, monkeypatch: MonkeyPatch) -> None:
        new_predefined_type_sets: dict[type[Any], set[Any]] = {
            **PREDEFINED_INSTANCE_SETS,
            int: {1, 2},
            str: {"a", "b"},
        }
        monkeypatch.setattr(
            type_sets, "PREDEFINED_INSTANCE_SETS", new_predefined_type_sets
        )

        expected_instances: tuple[list[int | str], ...] = (
            [1, "a"],
            [1, "b"],
            [2, "a"],
            [2, "b"],
        )
        expanded_type: ExpandedType[type[list[Any]]] = ExpandedType(list, (int, str))
        expanded_instances: tuple[list[Any], ...] = expanded_type.get_instances()
        for instance in expected_instances:
            assert instance in expanded_instances

    def test_get_instances_with_multiple_nested(self, monkeypatch: MonkeyPatch) -> None:
        new_predefined_type_sets: dict[type[Any], set[Any]] = {
            **PREDEFINED_INSTANCE_SETS,
            int: {1, 2},
            str: {"a", "b"},
        }
        monkeypatch.setattr(
            type_sets, "PREDEFINED_INSTANCE_SETS", new_predefined_type_sets
        )

        expected_instances: tuple[list[list[int] | str], ...] = (
            [[1], "a"],
            [[1], "b"],
            [[2], "a"],
            [[2], "b"],
        )
        expanded_type: ExpandedType[Any] = ExpandedType(
            list, (ExpandedType(list, (int,)), str)
        )
        expanded_instances: tuple[Any, ...] = expanded_type.get_instances()
        for instance in expected_instances:
            assert instance in expanded_instances

    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments", "expected_sets"],
        argvalues=[
            (
                List,
                (int,),
                [
                    PREDEFINED_INSTANCE_SETS[int],
                ],
            ),
            (
                Union,
                (int, str),
                [PREDEFINED_INSTANCE_SETS[int], PREDEFINED_INSTANCE_SETS[str]],
            ),
            (
                Tuple,
                (int, str),
                [PREDEFINED_INSTANCE_SETS[int], PREDEFINED_INSTANCE_SETS[str]],
            ),
        ],
        ids=["nested_param", "sum_param", "product_param"],
    )
    def test__get_instances_for_each_argument(
        self,
        base_type: type[T_co],
        type_arguments: tuple[Any, ...],
        expected_sets: tuple[set[Any], ...],
    ) -> None:
        expected: list[tuple[Any, ...]] = [
            tuple(iter(expected_set)) for expected_set in expected_sets
        ]
        assert (
            ExpandedType(
                base_type=base_type,
                type_arguments=type_arguments,
            )._get_instances_for_each_argument()
            == expected
        )

    @pytest.mark.parametrize(
        argnames=["instance_sets", "expected_combinations"],
        argvalues=[
            ([(1, 2)], [(1,), (2,)]),
            ([(1, 2), (3, 4)], [(1, 3), (1, 4), (2, 3), (2, 4)]),
        ],
        ids=[
            "single_set",
            "multiple_sets",
        ],
    )
    def test__get_combinations(
        self,
        instance_sets: list[tuple[T, ...]],
        expected_combinations: list[tuple[Any, ...]],
    ) -> None:
        assert ExpandedType._get_combinations(instance_sets) == expected_combinations

    @pytest.mark.parametrize(
        argnames=["base_type"],
        argvalues=[
            (type,),
        ],
        indirect=True,
    )
    def test__instantiate_combinations_with_builtin(
        self, expanded_type: ExpandedType[Any]
    ) -> None:
        with pytest.raises(ValueError):
            expanded_type._instantiate_combinations(
                argument_combinations=[("foo", "bar")]
            )

    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments", "combinations", "expected"],
        argvalues=[
            (lambda: None, tuple(), tuple(), tuple()),
            (list, (int,), ((1, 2),), ([1, 2],)),
            (
                lambda a, b, c: [a, b, c],
                (bool, bool, bool),
                ((True, False, True),),
                ([True, False, True],),
            ),
        ],
        ids=["no_parameters_sig", "one_parameter_sig", "many_parameters_sig"],
        indirect=["base_type", "type_arguments"],
    )
    def test__instantiate_from_signature(
        self,
        expanded_type: ExpandedType[T],
        combinations: list[tuple[Any, ...]],
        expected: tuple[T, ...],
    ) -> None:
        assert (
            expanded_type._instantiate_from_signature(
                argument_combinations=combinations
            )
            == expected
        )

    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments", "combinations", "expected"],
        argvalues=[
            (lambda: None, tuple(), tuple(), tuple()),
            (list, (int,), ((1, 2),), ([1, 2],)),
            (
                lambda a, b, c: [a, b, c],
                (bool, bool, bool),
                ((True, False, True),),
                ([True, False, True],),
            ),
        ],
        ids=["no_parameters_sig", "one_parameter_sig", "many_parameters_sig"],
        indirect=["base_type", "type_arguments"],
    )
    def test__instantiate_error_handler(
        self,
        expanded_type: ExpandedType[T],
        combinations: list[tuple[Any, ...]],
        expected: tuple[T, ...],
    ) -> None:
        assert (
            expanded_type._instantiate_error_handler(argument_combinations=combinations)
            == expected
        )

    def test__handle_multiple_signature(self) -> None:
        pass

    def test__handle_single_signature(self) -> None:
        pass

    def test__instantiate_complex_type(self) -> None:
        pass

    @pytest.mark.parametrize(
        argnames=["base_type", "type_arguments", "combination"],
        argvalues=[
            (list, (int,), (1, 2, 3)),
            (list, (int, str), (1, "2", 3)),
        ],
        ids=[
            "single_type_arg",
            "multiple_type_args",
        ],
        indirect=["base_type", "type_arguments"],
    )
    def test__instantiate_basic_type(
        self,
        expanded_type: ExpandedType[T],
        combination: tuple[Any, ...],
    ) -> None:
        assert expanded_type._instantiate_basic_type(
            arguments=combination
        ) == expanded_type.base_type(combination)


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        ((DummyClassNoArgs), {ExpandedType(DummyClassNoArgs, tuple())}),
        ((DummyClassNoArgs), {ExpandedType(DummyClassNoArgs, tuple())}),
    ],
)
def test_expand_type_with_non_supported_type(
    type_arg: type[T], expected: set[type[T]]
) -> None:
    assert expand_type(type_arg) == expected


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (int, {int}),
        (float, {float}),
        (complex, {complex}),
        (str, {str}),
        (bytes, {bytes}),
        (bool, {bool}),
        (type(None), {NoneType}),
    ],
)
def test_base_types(type_arg: type[T], expected: set[type[T]]) -> None:

    assert expand_type(type_arg) == expected


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (List[int], [ExpandedType(list, (int,))]),
        (List[List[int]], [ExpandedType(list, (ExpandedType(list, (int,)),))]),
        (Dict[str, int], [ExpandedType(dict, (str, int))]),
        (Dict[str, List[int]], [ExpandedType(dict, (str, ExpandedType(list, (int,))))]),
        (Tuple[int], [ExpandedType(tuple, (int,))]),
        (Tuple[int, str], [ExpandedType(tuple, (int, str))]),
        (Tuple[int, ...], [ExpandedType(tuple, (int, ...))]),
        (
            Tuple[int, Dict[str, int]],
            [ExpandedType(tuple, (int, ExpandedType(dict, (str, int))))],
        ),
        (
            Tuple[int, Union[float, str]],
            [ExpandedType(tuple, (int, float)), ExpandedType(tuple, (int, str))],
        ),
        (Set[str], [ExpandedType(set, (str,))]),
        (FrozenSet[str], [ExpandedType(frozenset, (str,))]),
    ],
    ids=lambda x: str(x),
)
def test_expand_type_with_product_types(
    type_arg: type[T], expected: Sequence[Any]
) -> None:

    assert expand_type(type_arg) == {*expected}


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (Union[int, str], [int, str]),
        (Union[int, str, float], [int, str, float]),
        (Optional[int], [int, NoneType]),
        (Optional[Optional[int]], [int, NoneType]),
        (Optional[Union[int, str]], [int, str, NoneType]),
    ],
    ids=lambda x: str(x),
)
def test_expand_type_with_sum_types(type_arg: type[T], expected: Sequence[Any]) -> None:

    assert expand_type(type_arg) == {*expected}


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (List[int], [ExpandedType(list, (int,))]),
        (List[List[int]], [ExpandedType(list, (ExpandedType(list, (int,)),))]),
        (Dict[str, int], [ExpandedType(dict, (str, int))]),
        (Dict[str, List[int]], [ExpandedType(dict, (str, ExpandedType(list, (int,))))]),
        (Tuple[int], [ExpandedType(tuple, (int,))]),
        (Tuple[int, str], [ExpandedType(tuple, (int, str))]),
        (Tuple[int, ...], [ExpandedType(tuple, (int, ...))]),
        (
            Tuple[int, Dict[str, int]],
            [ExpandedType(tuple, (int, ExpandedType(dict, (str, int))))],
        ),
    ],
    ids=lambda x: str(x),
)
def test_expand_type_with_recursive_types(
    type_arg: type[T], expected: Sequence[Any]
) -> None:
    assert expand_type(type_arg) == {*expected}


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (
            List[Union[str, int]],
            [ExpandedType(list, (str,)), ExpandedType(list, (int,))],
        ),
        (
            List[Union[str, int, float]],
            [
                ExpandedType(list, (str,)),
                ExpandedType(list, (int,)),
                ExpandedType(list, (float,)),
            ],
        ),
        (
            Union[List[str], List[int]],
            [ExpandedType(list, (str,)), ExpandedType(list, (int,))],
        ),
        (
            Union[List[str], List[int], List[float]],
            [
                ExpandedType(list, (str,)),
                ExpandedType(list, (int,)),
                ExpandedType(list, (float,)),
            ],
        ),
        (
            List[Union[Dict[str, int], Optional[int]]],
            [
                ExpandedType(list, (ExpandedType(dict, (str, int)),)),
                ExpandedType(list, (NoneType,)),
                ExpandedType(list, (int,)),
            ],
        ),
        (
            Union[Dict[str, int], Optional[int]],
            [ExpandedType(dict, (str, int)), NoneType, int],
        ),
        (
            List[Union[Dict[str, Optional[int]], Optional[int]]],
            [
                ExpandedType(list, (ExpandedType(dict, (str, int)),)),
                ExpandedType(list, (ExpandedType(dict, (str, NoneType)),)),
                ExpandedType(list, (NoneType,)),
                ExpandedType(list, (int,)),
            ],
        ),
        (
            List[Union[Dict[Union[str, int], Optional[int]], Optional[int]]],
            [
                ExpandedType(list, (ExpandedType(dict, (str, int)),)),
                ExpandedType(list, (ExpandedType(dict, (int, int)),)),
                ExpandedType(list, (ExpandedType(dict, (str, NoneType)),)),
                ExpandedType(list, (ExpandedType(dict, (int, NoneType)),)),
                ExpandedType(list, (NoneType,)),
                ExpandedType(list, (int,)),
            ],
        ),
    ],
    ids=lambda x: str(x),
)
def test_expand_type_with_combinations(
    type_arg: type[T], expected: Sequence[Any]
) -> None:
    assert expand_type(type_arg) == {*expected}


def test_optional_expansion() -> None:
    result: set[Any] = expand_type(Optional[int])
    assert NoneType in result
    assert int in result


def test_union_expansion() -> None:
    result: set[Any] = expand_type(Union[int, str])
    assert NoneType not in result
    assert int in result
    assert str in result


def test_expanded_type() -> None:
    result: set[ExpandedType[type[dict[str, int | None]]]] = expand_type(
        Dict[str, Optional[int]]
    )

    assert ExpandedType(dict, (str, int)) in result
    assert ExpandedType(dict, (str, NoneType)) in result
