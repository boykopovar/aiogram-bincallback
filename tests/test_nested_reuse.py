from pydantic import BaseModel

from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import plan_total_bits

from tests.conftest import planning_bfield


class Shared(BaseModel):
    value: int = planning_bfield(bits=10, signed=False)


def test_same_nested_model_reused_in_two_parents_builds_independent_plans():
    class ParentOne(BaseModel):
        shared: Shared
        extra: int = planning_bfield(bits=2, signed=False)

    class ParentTwo(BaseModel):
        shared: Shared
        extra: int = planning_bfield(bits=3, signed=False)

    plan_one = build_codec_plan(ParentOne)
    plan_two = build_codec_plan(ParentTwo)

    assert plan_total_bits(plan_one) == 10 + 2
    assert plan_total_bits(plan_two) == 10 + 3


def test_same_nested_model_reused_twice_in_one_parent():
    class Pair(BaseModel):
        first: Shared
        second: Shared

    plan = build_codec_plan(Pair)

    assert plan_total_bits(plan) == 10 + 10
    assert plan[0].path == "first"
    assert plan[1].path == "second"
