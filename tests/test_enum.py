from enum import Enum
from enum import IntEnum

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import DuplicateBinOrderError
from aiogram_bincallback.planning import EnumFieldCodec
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


class Priority(IntEnum):
    LOW = 0
    HIGH = 1


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


def test_str_enum_encodes_as_index_in_bin_order():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))

    plan = build_codec_plan(Model)

    assert plan == [
        EnumFieldCodec(
            name="status",
            path="status",
            bits=4,
            bin_order=(Status.ACTIVE, Status.DONE),
            enum_cls=Status,
            optional=False,
        )
    ]


def test_int_enum_encodes_as_index_in_bin_order():
    class Model(BaseModel):
        priority: Priority = planning_bfield(bits=1, bin_order=(Priority.LOW, Priority.HIGH))

    plan = build_codec_plan(Model)

    assert plan == [
        EnumFieldCodec(
            name="priority",
            path="priority",
            bits=1,
            bin_order=(Priority.LOW, Priority.HIGH),
            enum_cls=Priority,
            optional=False,
        )
    ]


def test_plain_enum_encodes_as_index_in_bin_order():
    class Model(BaseModel):
        direction: Direction = planning_bfield(
            bits=2,
            bin_order=(Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT),
        )

    plan = build_codec_plan(Model)

    assert plan == [
        EnumFieldCodec(
            name="direction",
            path="direction",
            bits=2,
            bin_order=(Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT),
            enum_cls=Direction,
            optional=False,
        )
    ]


def test_enum_bin_order_can_be_a_strict_subset_of_members():
    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=2, bin_order=(Direction.UP, Direction.DOWN, Direction.LEFT))

    plan = build_codec_plan(Model)

    assert plan[0].bin_order == (Direction.UP, Direction.DOWN, Direction.LEFT)


def test_enum_field_without_bin_order_defaults_to_declaration_order():
    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=2)

    plan = build_codec_plan(Model)

    assert plan[0].bin_order == (Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT)


def test_enum_field_without_bin_order_matches_explicit_full_order():
    class ModelDefault(BaseModel):
        status: Status = planning_bfield(bits=4)

    class ModelExplicit(BaseModel):
        status: Status = planning_bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))

    default_plan = build_codec_plan(ModelDefault)
    explicit_plan = build_codec_plan(ModelExplicit)

    assert default_plan[0].bin_order == explicit_plan[0].bin_order


def test_enum_bin_order_with_duplicate_member_raises_duplicate_bin_order_error():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE, Status.ACTIVE))

    with pytest.raises(DuplicateBinOrderError) as excinfo:
        build_codec_plan(Model)

    assert "status" in str(excinfo.value)
