import pytest
from aiogram.filters.callback_data import CallbackData

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import DecodeError
from aiogram_bincallback import PayloadCorruptError
from aiogram_bincallback import PrefixMismatchError
from aiogram_bincallback import bfield


class TextCb(CallbackData, prefix="text"):
    value: int


def test_binary_callback_data_is_a_callback_data_instance():
    class BinCb(BinaryCallbackData, prefix=4001, version=1):
        value: int = bfield(bits=8, signed=False)

    instance = BinCb(value=1)

    assert isinstance(instance, CallbackData)


def test_binary_unpack_raises_value_error_subclass_for_foreign_text_callback_data():
    class BinCb(BinaryCallbackData, prefix=4002, version=1):
        value: int = bfield(bits=8, signed=False)

    text_packed = TextCb(value=1).pack()

    with pytest.raises(ValueError):
        BinCb.unpack(text_packed)


def test_binary_unpack_error_on_foreign_data_is_catchable_as_type_or_value_error():
    class BinCb(BinaryCallbackData, prefix=4003, version=1):
        value: int = bfield(bits=8, signed=False)

    text_packed = TextCb(value=1).pack()

    try:
        BinCb.unpack(text_packed)
        matched = False
    except (TypeError, ValueError):
        matched = True

    assert matched


def test_text_unpack_does_not_accidentally_accept_binary_packed_data():
    class BinCb(BinaryCallbackData, prefix=4004, version=1):
        value: int = bfield(bits=8, signed=False)

    binary_packed = BinCb(value=1).pack()

    with pytest.raises((TypeError, ValueError)):
        TextCb.unpack(binary_packed)


def test_two_binary_classes_in_same_router_only_the_matching_prefix_unpacks():
    class RouterCbOne(BinaryCallbackData, prefix=4005, version=1):
        value: int = bfield(bits=8, signed=False)

    class RouterCbTwo(BinaryCallbackData, prefix=4006, version=1):
        value: int = bfield(bits=8, signed=False)

    packed_from_one = RouterCbOne(value=9).pack()

    restored = RouterCbOne.unpack(packed_from_one)
    assert restored.value == 9

    with pytest.raises(PrefixMismatchError):
        RouterCbTwo.unpack(packed_from_one)


def test_unpack_wraps_unexpected_non_binary_callback_errors_as_decode_error():
    class WrapCb(BinaryCallbackData, prefix=4007, version=1):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises((DecodeError, PayloadCorruptError)):
        WrapCb.unpack("not a valid base93 payload \" \\")
