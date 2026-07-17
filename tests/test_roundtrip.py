from enum import Enum
from typing import Optional

from pydantic import BaseModel

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


def test_flat_model_packs_to_string_and_unpacks_to_equal_instance():
    class FlatCb(BinaryCallbackData, prefix=1001, version=1):
        item_count: int = bfield(bits=8, signed=False)
        status: Status = bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))

    original = FlatCb(item_count=42, status=Status.DONE)

    packed = original.pack()
    restored = FlatCb.unpack(packed)

    assert isinstance(packed, str)
    assert restored == original


def test_pack_output_respects_telegram_callback_data_length_limit():
    class SmallCb(BinaryCallbackData, prefix=1002, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = SmallCb(value=200).pack()

    assert len(packed.encode("utf-8")) <= 64


def test_signed_negative_value_roundtrips():
    class SignedCb(BinaryCallbackData, prefix=1003, version=1):
        delta: int = bfield(bits=8, signed=True)

    original = SignedCb(delta=-100)

    restored = SignedCb.unpack(original.pack())

    assert restored.delta == -100


def test_optional_field_present_roundtrips_value():
    class OptionalPresentCb(BinaryCallbackData, prefix=1004, version=1):
        coupon_id: Optional[int] = bfield(bits=16, signed=False)

    original = OptionalPresentCb(coupon_id=555)

    restored = OptionalPresentCb.unpack(original.pack())

    assert restored.coupon_id == 555


def test_optional_field_absent_roundtrips_as_none():
    class OptionalAbsentCb(BinaryCallbackData, prefix=1005, version=1):
        coupon_id: Optional[int] = bfield(bits=16, signed=False)

    original = OptionalAbsentCb(coupon_id=None)

    restored = OptionalAbsentCb.unpack(original.pack())

    assert restored.coupon_id is None


def test_nested_basemodel_roundtrips_all_its_fields():
    class CartTotals(BaseModel):
        subtotal: int = bfield(bits=32, signed=False)
        discount: int = bfield(bits=32, signed=False)
        coupon_id: Optional[int] = bfield(bits=16, signed=False)

    class OrderCb(BinaryCallbackData, prefix=1006, version=1):
        item_count: int = bfield(bits=8, signed=False)
        totals: CartTotals

    original = OrderCb(
        item_count=3,
        totals=CartTotals(subtotal=123456, discount=987654, coupon_id=None),
    )

    restored = OrderCb.unpack(original.pack())

    assert restored == original


def test_bool_field_roundtrips_both_values():
    class BoolCb(BinaryCallbackData, prefix=1007, version=1):
        flag: bool = bfield()

    assert BoolCb.unpack(BoolCb(flag=True).pack()).flag is True
    assert BoolCb.unpack(BoolCb(flag=False).pack()).flag is False


def test_zero_prefix_and_zero_version_are_valid_and_roundtrip():
    class ZeroCb(BinaryCallbackData, prefix=0, version=0):
        value: int = bfield(bits=4, signed=False)

    restored = ZeroCb.unpack(ZeroCb(value=7).pack())

    assert restored.value == 7


def test_two_independent_instances_of_same_class_pack_differently():
    class DistinctCb(BinaryCallbackData, prefix=1008, version=1):
        value: int = bfield(bits=8, signed=False)

    first_packed = DistinctCb(value=1).pack()
    second_packed = DistinctCb(value=2).pack()

    assert first_packed != second_packed
