from enum import Enum
from enum import IntEnum
from typing import List
from typing import Optional

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import BitsNotApplicableToListError
from aiogram_bincallback.core import DuplicateBinOrderError
from aiogram_bincallback.core import MissingMaxLenError
from aiogram_bincallback.core import SignedNotApplicableError
from aiogram_bincallback.core import UnsupportedFieldTypeError
from aiogram_bincallback.planning import EnumListFieldCodec
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import build_primitive_codec
from aiogram_bincallback.planning import plan_total_bits

from tests.conftest import planning_bfield


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class Priority(IntEnum):
    LOW = 0
    HIGH = 1


def test_enum_list_field_builds_enum_list_codec():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)

    assert plan == [
        EnumListFieldCodec(
            name="path",
            path="path",
            item_bits=2,
            len_bits=3,
            max_len=5,
            bin_order=(Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT),
            enum_cls=Direction,
            optional=False,
        )
    ]


def test_enum_list_field_without_bin_order_defaults_to_declaration_order():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3)

    plan = build_codec_plan(Model)

    assert plan[0].bin_order == (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)


def test_enum_list_field_respects_explicit_bin_order():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3, bin_order=(Direction.LEFT, Direction.RIGHT))

    plan = build_codec_plan(Model)

    assert plan[0].bin_order == (Direction.LEFT, Direction.RIGHT)
    assert plan[0].item_bits == 1


def test_enum_list_field_without_max_len_raises_missing_max_len_error():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield()

    with pytest.raises(MissingMaxLenError) as excinfo:
        build_codec_plan(Model)

    assert "path" in str(excinfo.value)


def test_enum_list_field_with_bits_raises_bits_not_applicable_to_list_error():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3, bits=4)

    with pytest.raises(BitsNotApplicableToListError) as excinfo:
        build_codec_plan(Model)

    assert "path" in str(excinfo.value)


def test_enum_list_field_with_signed_raises_signed_not_applicable_error():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3, signed=False)

    with pytest.raises(SignedNotApplicableError):
        build_codec_plan(Model)


def test_enum_list_field_with_duplicate_bin_order_raises_duplicate_bin_order_error():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3, bin_order=(Direction.UP, Direction.UP))

    with pytest.raises(DuplicateBinOrderError):
        build_codec_plan(Model)


def test_list_of_optional_enum_raises_unsupported_field_type_error():
    class Model(BaseModel):
        path: List[Optional[Direction]] = planning_bfield(max_len=3)

    with pytest.raises(UnsupportedFieldTypeError) as excinfo:
        build_codec_plan(Model)

    assert "path" in str(excinfo.value)


def test_list_of_non_enum_raises_unsupported_field_type_error():
    class Model(BaseModel):
        values: List[int] = planning_bfield(max_len=3)

    with pytest.raises(UnsupportedFieldTypeError):
        build_codec_plan(Model)


def test_unrelated_type_annotation_raises_unsupported_field_type_error():
    class Model(BaseModel):
        value: str = planning_bfield()

    with pytest.raises(UnsupportedFieldTypeError):
        build_codec_plan(Model)


def test_optional_enum_list_field_is_marked_optional():
    class Model(BaseModel):
        path: Optional[List[Direction]] = planning_bfield(max_len=3)

    plan = build_codec_plan(Model)

    assert plan[0].optional is True


def test_optional_enum_list_adds_exactly_one_presence_bit():
    class Model(BaseModel):
        path: Optional[List[Direction]] = planning_bfield(max_len=3, bin_order=(Direction.UP, Direction.DOWN))

    plan = build_codec_plan(Model)

    without_presence = plan_total_bits(
        build_codec_plan(
            type(
                "Required",
                (BaseModel,),
                {
                    "__annotations__": {"path": List[Direction]},
                    "path": planning_bfield(max_len=3, bin_order=(Direction.UP, Direction.DOWN)),
                },
            )
        )
    )

    assert plan_total_bits(plan) == 1 + without_presence


def test_enum_list_total_bits_accounts_for_worst_case_max_len():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)

    len_bits = 3
    item_bits = 2
    assert plan_total_bits(plan) == len_bits + 5 * item_bits


def test_enum_list_len_bits_covers_zero_to_max_len_inclusive():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=7)

    plan = build_codec_plan(Model)

    assert plan[0].len_bits == 3


def test_enum_list_len_bits_for_max_len_that_is_power_of_two_minus_one():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=1)

    plan = build_codec_plan(Model)

    assert plan[0].len_bits == 1


def test_enum_list_field_with_int_enum_members():
    class Model(BaseModel):
        priorities: List[Priority] = planning_bfield(max_len=4)

    plan = build_codec_plan(Model)

    assert plan[0].bin_order == (Priority.LOW, Priority.HIGH)
    assert plan[0].item_bits == 1


def test_build_primitive_codec_builds_enum_list_codec_directly():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3, bin_order=(Direction.UP, Direction.DOWN))

    codec = build_primitive_codec("path", Model.model_fields["path"], "path")

    assert codec == EnumListFieldCodec(
        name="path",
        path="path",
        item_bits=1,
        len_bits=2,
        max_len=3,
        bin_order=(Direction.UP, Direction.DOWN),
        enum_cls=Direction,
        optional=False,
    )
