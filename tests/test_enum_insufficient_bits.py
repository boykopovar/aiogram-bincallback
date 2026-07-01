from enum import Enum

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import InsufficientBitsError
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


def test_enum_field_with_too_few_bits_raises_insufficient_bits_error():
    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=1, bin_order=("UP", "DOWN", "LEFT", "RIGHT"))

    with pytest.raises(InsufficientBitsError) as excinfo:
        build_codec_plan(Model)

    assert "direction" in str(excinfo.value)


def test_enum_field_with_exactly_enough_bits_does_not_raise():
    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=2, bin_order=("UP", "DOWN", "LEFT", "RIGHT"))

    plan = build_codec_plan(Model)

    assert plan[0].bits == 2


def test_enum_field_with_single_member_and_zero_bits_is_valid():
    class Direction(Enum):
        UP = "up"

    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=0, bin_order=("UP",))

    plan = build_codec_plan(Model)

    assert plan[0].bits == 0


def test_enum_field_with_single_member_and_negative_bits_raises_insufficient_bits_error():
    class Direction(Enum):
        UP = "up"

    class Model(BaseModel):
        direction: Direction = planning_bfield(bits=-1, bin_order=("UP",))

    with pytest.raises(InsufficientBitsError):
        build_codec_plan(Model)
