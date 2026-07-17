from enum import Enum
from typing import List
from typing import Optional

import pytest
from pydantic import BaseModel

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import PrefixEnumMismatchError
from aiogram_bincallback import bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


class ActionPrefix(Enum):
    OPEN = 2001
    CLOSE = 2002


class FlatCb(BinaryCallbackData, prefix=2001, version=1):
    item_count: int = bfield(bits=8, signed=False)
    status: Status = bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))


class CloseCb(BinaryCallbackData, prefix=2002, version=1):
    value: int = bfield(bits=8, signed=False)


def test_flat_model_describes_prefix_and_values_without_enum():
    described = FlatCb(item_count=42, status=Status.DONE).describe()

    assert described == "2001:42:DONE"


def test_flat_model_describes_prefix_as_enum_member_name():
    described = FlatCb(item_count=42, status=Status.DONE).describe(ActionPrefix)

    assert described == "OPEN:42:DONE"


def test_describe_uses_correct_enum_member_for_each_prefix():
    described_open = FlatCb(item_count=1, status=Status.ACTIVE).describe(ActionPrefix)
    described_close = CloseCb(value=1).describe(ActionPrefix)

    assert described_open == "OPEN:1:ACTIVE"
    assert described_close == "CLOSE:1"


def test_describe_raises_when_prefix_enum_has_no_matching_member():
    class UnmappedCb(BinaryCallbackData, prefix=9999, version=1):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises(PrefixEnumMismatchError):
        UnmappedCb(value=1).describe(ActionPrefix)


def test_describe_renders_bool_field_as_int_by_default():
    class BoolCb(BinaryCallbackData, prefix=2003, version=1):
        flag: bool = bfield()

    assert BoolCb(flag=True).describe() == "2003:1"
    assert BoolCb(flag=False).describe() == "2003:0"


def test_describe_renders_bool_field_as_python_bool_string_when_disabled():
    class BoolCb(BinaryCallbackData, prefix=2013, version=1):
        flag: bool = bfield()

    described = BoolCb(flag=True).describe(bool_as_int=False)
    assert described == "2013:True"

    described = BoolCb(flag=False).describe(bool_as_int=False)
    assert described == "2013:False"


def test_describe_renders_enum_field_as_value_when_enum_as_name_disabled():
    described = FlatCb(item_count=42, status=Status.DONE).describe(enum_as_name=False)

    assert described == "2001:42:done"


def test_describe_bool_as_int_and_enum_as_name_are_independent():
    class MixedCb(BinaryCallbackData, prefix=2014, version=1):
        item_count: int = bfield(bits=8, signed=False)
        status: Status = bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))
        flag: bool = bfield()

    instance = MixedCb(item_count=1, status=Status.ACTIVE, flag=True)

    assert instance.describe() == "2014:1:ACTIVE:1"
    assert instance.describe(bool_as_int=False) == "2014:1:ACTIVE:True"
    assert instance.describe(enum_as_name=False) == "2014:1:active:1"
    assert instance.describe(bool_as_int=False, enum_as_name=False) == "2014:1:active:True"


def test_describe_bool_as_int_applies_inside_nested_basemodel():
    class NestedFlags(BaseModel):
        seen: bool = bfield()

    class NestedFlagCb(BinaryCallbackData, prefix=2015, version=1):
        state: NestedFlags

    instance = NestedFlagCb(state=NestedFlags(seen=True))

    assert instance.describe() == "2015:1"
    assert instance.describe(bool_as_int=False) == "2015:True"


def test_describe_renders_signed_negative_value():
    class SignedCb(BinaryCallbackData, prefix=2004, version=1):
        delta: int = bfield(bits=8, signed=True)

    assert SignedCb(delta=-100).describe() == "2004:-100"


def test_describe_renders_present_optional_field_value():
    class OptionalCb(BinaryCallbackData, prefix=2005, version=1):
        coupon_id: Optional[int] = bfield(bits=16, signed=False)

    assert OptionalCb(coupon_id=555).describe() == "2005:555"


def test_describe_renders_absent_optional_field_as_none():
    class OptionalCb(BinaryCallbackData, prefix=2006, version=1):
        coupon_id: Optional[int] = bfield(bits=16, signed=False)

    assert OptionalCb(coupon_id=None).describe() == "2006:None"


def test_describe_flattens_nested_basemodel_fields_in_declared_order():
    class CartTotals(BaseModel):
        subtotal: int = bfield(bits=32, signed=False)
        discount: int = bfield(bits=32, signed=False)

    class OrderCb(BinaryCallbackData, prefix=2007, version=1):
        item_count: int = bfield(bits=8, signed=False)
        totals: CartTotals

    described = OrderCb(
        item_count=3,
        totals=CartTotals(subtotal=123456, discount=987654),
    ).describe()

    assert described == "2007:3:123456:987654"


def test_describe_on_base_class_itself_raises_type_error():
    with pytest.raises(TypeError):
        BinaryCallbackData.describe(BinaryCallbackData)


def test_describe_does_not_mutate_or_require_pack():
    class ValueCb(BinaryCallbackData, prefix=2008, version=1):
        value: int = bfield(bits=8, signed=False)

    instance = ValueCb(value=7)

    assert instance.describe() == "2008:7"
    assert instance.value == 7


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


class RouteCb(BinaryCallbackData, prefix=2009, version=1):
    path: List[Direction] = bfield(max_len=4)


def test_describe_wraps_enum_list_in_brackets_by_default():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe()

    assert described == "2009:[UP,DOWN]"


def test_describe_renders_enum_list_values_when_enum_list_as_name_disabled():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe(enum_list_as_name=False)

    assert described == "2009:[up,down]"


def test_describe_uses_custom_enum_list_separator():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe(enum_list_separator="|")

    assert described == "2009:[UP|DOWN]"


def test_describe_omits_enum_list_brackets_when_disabled():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe(enum_list_brackets=False)

    assert described == "2009:UP,DOWN"


def test_describe_enum_list_with_empty_separator_and_no_brackets():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe(
        enum_list_as_name=False,
        enum_list_separator="",
        enum_list_brackets=False,
    )

    assert described == "2009:updown"


def test_describe_enum_list_options_are_independent_of_enum_as_name():
    described = RouteCb(path=[Direction.UP, Direction.DOWN]).describe(enum_as_name=False)

    assert described == "2009:[UP,DOWN]"


def test_describe_enum_list_options_apply_inside_nested_basemodel():
    class NestedRoute(BaseModel):
        path: List[Direction] = bfield(max_len=4)

    class NestedRouteCb(BinaryCallbackData, prefix=2010, version=1):
        route: NestedRoute

    instance = NestedRouteCb(route=NestedRoute(path=[Direction.LEFT, Direction.RIGHT]))

    assert instance.describe() == "2010:[LEFT,RIGHT]"
    assert instance.describe(enum_list_brackets=False) == "2010:LEFT,RIGHT"
