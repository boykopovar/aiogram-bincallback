from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import bfield
from aiogram_bincallback.config import get_cipher
from aiogram_bincallback.config import get_wire_codec
from aiogram_bincallback.header import encode_header


class FirstKindCb(BinaryCallbackData, prefix=9801, version=1):
    value: int = bfield(bits=8, signed=False)


class SecondKindCb(BinaryCallbackData, prefix=9802, version=1):
    label: int = bfield(bits=8, signed=False)


def test_try_unpack_returns_instance_of_matching_registered_class():
    packed = FirstKindCb(value=7).pack()

    resolved = BinaryCallbackData.try_unpack(packed)

    assert isinstance(resolved, FirstKindCb)
    assert resolved.value == 7


def test_try_unpack_picks_correct_class_among_several_registered():
    packed_first = FirstKindCb(value=1).pack()
    packed_second = SecondKindCb(label=2).pack()

    resolved_first = BinaryCallbackData.try_unpack(packed_first)
    resolved_second = BinaryCallbackData.try_unpack(packed_second)

    assert isinstance(resolved_first, FirstKindCb)
    assert isinstance(resolved_second, SecondKindCb)


def test_try_unpack_returns_none_for_unregistered_prefix():
    raw_header = encode_header(prefix=9803, version=1)
    packed = get_wire_codec().encode(get_cipher().encrypt(raw_header))

    resolved = BinaryCallbackData.try_unpack(packed)

    assert resolved is None


def test_try_unpack_returns_none_for_garbage_string():
    resolved = BinaryCallbackData.try_unpack("not-a-valid-payload")

    assert resolved is None


def test_try_unpack_returns_none_for_empty_string():
    resolved = BinaryCallbackData.try_unpack("")

    assert resolved is None
