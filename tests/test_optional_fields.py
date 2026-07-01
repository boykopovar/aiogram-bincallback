from typing import Optional

from pydantic import BaseModel

from aiogram_bincallback.planning import BoolFieldCodec
from aiogram_bincallback.planning import IntFieldCodec
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import plan_total_bits

from tests.conftest import planning_bfield


def test_optional_primitive_field_is_marked_optional():
    class Model(BaseModel):
        value: Optional[int] = planning_bfield(bits=16, signed=False)

    plan = build_codec_plan(Model)

    assert plan == [IntFieldCodec(name="value", path="value", bits=16, signed=False, optional=True)]


def test_required_field_has_no_presence_bit():
    class Model(BaseModel):
        value: int = planning_bfield(bits=16, signed=False)

    plan = build_codec_plan(Model)

    assert plan_total_bits(plan) == 16


def test_optional_field_adds_exactly_one_presence_bit():
    class Model(BaseModel):
        value: Optional[int] = planning_bfield(bits=16, signed=False)

    plan = build_codec_plan(Model)

    assert plan_total_bits(plan) == 1 + 16


def test_optional_bool_field_adds_presence_bit_on_top_of_default_bool_bit():
    class Model(BaseModel):
        flag: Optional[bool] = planning_bfield()

    plan = build_codec_plan(Model)

    assert plan == [BoolFieldCodec(name="flag", path="flag", optional=True)]
    assert plan_total_bits(plan) == 1 + 1


def test_optional_nested_basemodel_saves_full_tail_when_none():
    class Inner(BaseModel):
        a: int = planning_bfield(bits=10, signed=False)
        b: int = planning_bfield(bits=20, signed=False)

    class Outer(BaseModel):
        inner: Optional[Inner]

    plan = build_codec_plan(Outer)

    assert plan_total_bits(plan) == 1 + (10 + 20)


def test_optional_nested_basemodel_keeps_its_own_optional_fields_independent():
    class Inner(BaseModel):
        maybe: Optional[int] = planning_bfield(bits=5, signed=False)
        required: int = planning_bfield(bits=6, signed=False)

    class Outer(BaseModel):
        inner: Optional[Inner]

    plan = build_codec_plan(Outer)

    assert plan_total_bits(plan) == 1 + (1 + 5 + 6)
