from pydantic import BaseModel

from aiogram_bincallback.planning import IntFieldCodec
from aiogram_bincallback.planning import NestedFieldCodec
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import plan_total_bits

from tests.conftest import planning_bfield


class CartTotals(BaseModel):
    subtotal: int = planning_bfield(bits=32, signed=False)
    discount: int = planning_bfield(bits=32, signed=False)


def test_nested_basemodel_produces_nested_field_codec_with_recursive_plan():
    class OrderCb(BaseModel):
        item_count: int = planning_bfield(bits=8, signed=False)
        totals: CartTotals

    plan = build_codec_plan(OrderCb)

    assert plan[0] == IntFieldCodec(name="item_count", path="item_count", bits=8, signed=False, optional=False)
    nested = plan[1]
    assert isinstance(nested, NestedFieldCodec)
    assert nested.name == "totals"
    assert nested.path == "totals"
    assert nested.model_cls is CartTotals
    assert nested.optional is False


def test_nested_basemodel_paths_are_dotted():
    class OrderCb(BaseModel):
        totals: CartTotals

    plan = build_codec_plan(OrderCb)
    nested = plan[0]

    assert [codec.path for codec in nested.plan] == ["totals.subtotal", "totals.discount"]


def test_nested_basemodel_bits_are_summed_recursively():
    class OrderCb(BaseModel):
        item_count: int = planning_bfield(bits=8, signed=False)
        totals: CartTotals

    plan = build_codec_plan(OrderCb)

    assert plan_total_bits(plan) == 8 + 32 + 32
