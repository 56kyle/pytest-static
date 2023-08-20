from types import NoneType
from typing import Any
from typing import Dict
from typing import FrozenSet
from typing import List
from typing import Literal
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

import pytest
from _pytest.monkeypatch import MonkeyPatch

from pytest_static.parametric import Config
from pytest_static.parametric import ExpandedType
from pytest_static.parametric import expand_type
from pytest_static.type_sets import PREDEFINED_TYPE_SETS


T = TypeVar("T")


class DummyClass:
    pass


class TestExpandedType:
    def test_get_instances_with_basic(self) -> None:
        expanded_type = ExpandedType(list, (int,))
        assert expanded_type.get_instances() == tuple(
            [value] for value in PREDEFINED_TYPE_SETS[int]
        )

    def test_get_instances_with_nested(self) -> None:
        expanded_type = ExpandedType(list, (ExpandedType(list, (int,)),))
        assert expanded_type.get_instances() == tuple(
            [[value]] for value in PREDEFINED_TYPE_SETS[int]
        )

    def test_get_instances_with_multiple(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setitem(PREDEFINED_TYPE_SETS, int, {1, 2})
        monkeypatch.setitem(PREDEFINED_TYPE_SETS, str, {"a", "b"})
        expected_instances: Tuple[List[Union[int, str]], ...] = (
            [1, "a"],
            [1, "b"],
            [2, "a"],
            [2, "b"],
        )
        expanded_type: ExpandedType[List[Any]] = ExpandedType(list, (int, str))
        expanded_instances: Tuple[List[Any], ...] = expanded_type.get_instances()
        for instance in expected_instances:
            assert instance in expanded_instances

    def test_get_instances_with_multiple_nested(self, monkeypatch: MonkeyPatch) -> None:
        monkeypatch.setitem(PREDEFINED_TYPE_SETS, int, {1, 2})
        monkeypatch.setitem(PREDEFINED_TYPE_SETS, str, {"a", "b"})
        expected_instances: Tuple[List[Union[List[int], str]], ...] = (
            [[1], "a"],
            [[1], "b"],
            [[2], "a"],
            [[2], "b"],
        )
        expanded_type = ExpandedType(list, (ExpandedType(list, (int,)), str))
        expanded_instances: Tuple[List[Any], ...] = expanded_type.get_instances()
        for instance in expected_instances:
            assert instance in expanded_instances

    @pytest.mark.parametrize(
        argnames=["primary_type", "type_args", "expected_sets"],
        argvalues=[
            (
                List,
                (int,),
                [
                    PREDEFINED_TYPE_SETS[int],
                ],
            ),
            (Union, (int, str), [PREDEFINED_TYPE_SETS[int], PREDEFINED_TYPE_SETS[str]]),
            (Tuple, (int, str), [PREDEFINED_TYPE_SETS[int], PREDEFINED_TYPE_SETS[str]]),
        ],
        ids=["nested_param", "sum_param", "product_param"],
    )
    def test__get_parameter_instance_sets(
        self,
        primary_type: Type[T],
        type_args: Type[T],
        expected_sets: Tuple[Set[Any], ...],
    ) -> None:
        expected_sets = [tuple(expected_set) for expected_set in expected_sets]
        assert (
            ExpandedType(
                primary_type=primary_type,
                type_args=type_args,
            )._get_parameter_instance_sets()
            == expected_sets
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
    def test__get_parameter_combinations(
        self,
        instance_sets: List[Tuple[T, ...]],
        expected_combinations: List[Tuple[Any, ...]],
    ) -> None:
        assert (
            ExpandedType._get_parameter_combinations(instance_sets)
            == expected_combinations
        )

    def test__instantiate_each_parameter_combination(self) -> None:
        pass

    def test__instantiate_from_signature(self) -> None:
        pass

    def test__instantiate_from_trial_and_error(self) -> None:
        pass

    def test__instantiate_combinations_using_expanded(self) -> None:
        pass

    def test__instantiate_combinations_using_not_expanded(self) -> None:
        pass

    def test__instantiate_expanded(self) -> None:
        pass

    def test__instantiate_not_expanded(
        self,
        expanded_type: ExpandedType,
    ) -> None:
        pass


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        ((DummyClass), {DummyClass}),
    ],
)
def test_expand_type_with_non_supported_type(
    type_arg: Type[T], expected: Set[Type[T]]
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
def test_base_types(type_arg: Type[T], expected: Set[Type[T]]) -> None:

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
    type_arg: Type[T], expected: Sequence[Any]
) -> None:

    assert expand_type(type_arg) == {*expected}


@pytest.mark.parametrize(
    argnames=["type_arg", "expected"],
    argvalues=[
        (Union[int, str], [int, str]),
        (Union[int, str, float], [int, str, float]),
        (Literal["a", "b", "c"], [Literal["a", "b", "c"]]),
        (Optional[int], [int, NoneType]),
        (Optional[Optional[int]], [int, NoneType]),
        (Optional[Union[int, str]], [int, str, NoneType]),
    ],
    ids=lambda x: str(x),
)
def test_expand_type_with_sum_types(type_arg: Type[T], expected: Sequence[Any]) -> None:

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
    type_arg: Type[T], expected: Sequence[Any]
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
    type_arg: Type[T], expected: Sequence[Any]
) -> None:
    assert expand_type(type_arg) == {*expected}


def test_optional_expansion() -> None:
    result: Set[Union[Any, ExpandedType[Any]]] = expand_type(Optional[int])
    assert NoneType in result
    assert int in result


def test_union_expansion() -> None:
    result: Set[Union[Any, ExpandedType[Any]]] = expand_type(Union[int, str])
    assert NoneType not in result
    assert int in result
    assert str in result


def test_expanded_type() -> None:
    result: Set[Union[Any, ExpandedType[Any]]] = expand_type(Dict[str, Optional[int]])
    assert ExpandedType(dict, (str, int)) in result
    assert ExpandedType(dict, (str, NoneType)) in result


def test_custom_handler() -> None:
    def custom_handler(
        type_arg: Type[T], config: Config
    ) -> Set[Union[Any, ExpandedType[T]]]:
        return {int}

    config: Config = Config(max_elements=5, custom_handlers={list: custom_handler})
    assert expand_type(List[str], config) == {int}
