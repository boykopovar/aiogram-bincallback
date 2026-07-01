from enum import Enum
from typing import Optional

import pytest
from pydantic import BaseModel

from aiogram_bincallback.codec import decode_fields
from aiogram_bincallback.codec import encode_fields
from aiogram_bincallback.core import ValueOverflowError
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


def test_flat_model_roundtrips_through_encode_and_decode():
    class Model(BaseModel):
        flag: bool = planning_bfield()
        value: int = planning_bfield(bits=16, signed=False)
        signed_value: int = planning_bfield(bits=8, signed=True)

    plan = build_codec_plan(Model)
    instance = Model(flag=True, value=12345, signed_value=-42)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"flag": True, "value": 12345, "signed_value": -42}
    assert new_bit_position == 1 + 16 + 8


def test_optional_field_present_roundtrips_its_value():
    class Model(BaseModel):
        value: Optional[int] = planning_bfield(bits=10, signed=False)

    plan = build_codec_plan(Model)
    instance = Model(value=777)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"value": 777}
    assert new_bit_position == 1 + 10


def test_optional_field_absent_skips_its_payload_bits():
    class Model(BaseModel):
        value: Optional[int] = planning_bfield(bits=10, signed=False)

    plan = build_codec_plan(Model)
    instance = Model(value=None)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"value": None}
    assert new_bit_position == 1


def test_enum_field_roundtrips_via_bin_order_index():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4, bin_order=(Status.ACTIVE, Status.DONE))

    plan = build_codec_plan(Model)
    instance = Model(status=Status.DONE)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"status": Status.DONE}
    assert new_bit_position == 4


def test_enum_field_without_bin_order_roundtrips_using_declaration_order():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4)

    plan = build_codec_plan(Model)
    instance = Model(status=Status.DONE)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"status": Status.DONE}
    assert new_bit_position == 4


def test_nested_basemodel_shares_one_bitstream_without_byte_padding():
    class Inner(BaseModel):
        a: int = planning_bfield(bits=3, signed=False)
        b: int = planning_bfield(bits=5, signed=False)

    class Outer(BaseModel):
        flag: bool = planning_bfield()
        inner: Inner

    plan = build_codec_plan(Outer)
    instance = Outer(flag=True, inner=Inner(a=5, b=17))

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"flag": True, "inner": {"a": 5, "b": 17}}
    assert new_bit_position == 1 + 3 + 5


def test_optional_nested_basemodel_absent_skips_full_inner_plan():
    class Inner(BaseModel):
        a: int = planning_bfield(bits=3, signed=False)
        b: int = planning_bfield(bits=5, signed=False)

    class Outer(BaseModel):
        inner: Optional[Inner]

    plan = build_codec_plan(Outer)
    instance = Outer(inner=None)

    data = encode_fields(plan, instance)
    decoded, new_bit_position = decode_fields(plan, data, 0)

    assert decoded == {"inner": None}
    assert new_bit_position == 1


def test_decode_fields_starts_reading_at_given_bit_offset():
    class Model(BaseModel):
        value: int = planning_bfield(bits=12, signed=False)

    plan = build_codec_plan(Model)
    instance = Model(value=999)
    payload = encode_fields(plan, instance)
    prefixed = b"\x00" + payload

    decoded, new_bit_position = decode_fields(plan, prefixed, 8)

    assert decoded == {"value": 999}
    assert new_bit_position == 8 + 12


def test_unsigned_overflow_raises_value_overflow_error():
    class Model(BaseModel):
        value: int = planning_bfield(bits=4, signed=False)

    plan = build_codec_plan(Model)
    instance = Model(value=100)

    with pytest.raises(ValueOverflowError) as excinfo:
        encode_fields(plan, instance)

    assert "value" in str(excinfo.value)


def test_unsigned_boundary_values_do_not_overflow():
    class Model(BaseModel):
        value: int = planning_bfield(bits=4, signed=False)

    plan = build_codec_plan(Model)

    encode_fields(plan, Model(value=0))
    encode_fields(plan, Model(value=15))
    with pytest.raises(ValueOverflowError):
        encode_fields(plan, Model(value=-1))
    with pytest.raises(ValueOverflowError):
        encode_fields(plan, Model(value=16))


def test_signed_boundary_values_do_not_overflow():
    class Model(BaseModel):
        value: int = planning_bfield(bits=8, signed=True)

    plan = build_codec_plan(Model)

    encode_fields(plan, Model(value=127))
    encode_fields(plan, Model(value=-128))
    with pytest.raises(ValueOverflowError):
        encode_fields(plan, Model(value=128))
    with pytest.raises(ValueOverflowError):
        encode_fields(plan, Model(value=-129))
