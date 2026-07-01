import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import ValueOverflowError
from aiogram_bincallback import bfield


def test_pack_raises_value_overflow_error_when_unsigned_value_exceeds_bits():
    class UnsignedCb(BinaryCallbackData, prefix=2001, version=1):
        value: int = bfield(bits=4, signed=False)

    instance = UnsignedCb.model_construct(value=16)

    with pytest.raises(ValueOverflowError) as excinfo:
        instance.pack()

    assert "value" in str(excinfo.value)


def test_pack_raises_value_overflow_error_when_signed_value_exceeds_positive_bound():
    class SignedCb(BinaryCallbackData, prefix=2002, version=1):
        value: int = bfield(bits=8, signed=True)

    instance = SignedCb.model_construct(value=128)

    with pytest.raises(ValueOverflowError):
        instance.pack()


def test_pack_raises_value_overflow_error_when_signed_value_exceeds_negative_bound():
    class SignedNegativeCb(BinaryCallbackData, prefix=2003, version=1):
        value: int = bfield(bits=8, signed=True)

    instance = SignedNegativeCb.model_construct(value=-129)

    with pytest.raises(ValueOverflowError):
        instance.pack()


def test_pack_succeeds_at_exact_unsigned_upper_boundary():
    class BoundaryCb(BinaryCallbackData, prefix=2004, version=1):
        value: int = bfield(bits=4, signed=False)

    instance = BoundaryCb(value=15)

    packed = instance.pack()

    assert BoundaryCb.unpack(packed).value == 15


def test_pack_raises_value_overflow_error_on_nested_model_field():
    from pydantic import BaseModel

    class Inner(BaseModel):
        value: int = bfield(bits=4, signed=False)

    class NestedOverflowCb(BinaryCallbackData, prefix=2005, version=1):
        inner: Inner

    instance = NestedOverflowCb.model_construct(inner=Inner.model_construct(value=99))

    with pytest.raises(ValueOverflowError):
        instance.pack()
