from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import bfield
from aiogram_bincallback.core import HEADER_BITS
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS
from aiogram_bincallback.wire import MAX_TOTAL_BITS


class EmptyMaxBitsCb(BinaryCallbackData, prefix=8801, version=1):
    pass


class FieldMaxBitsCb(BinaryCallbackData, prefix=8802, version=1):
    value: int = bfield(bits=8, signed=False)


def test_max_payload_bits_matches_wire_constant():
    assert EmptyMaxBitsCb.max_payload_bits() == MAX_PAYLOAD_BITS


def test_max_total_bits_matches_wire_constant():
    assert EmptyMaxBitsCb.max_total_bits() == MAX_TOTAL_BITS


def test_max_total_bits_equals_payload_bits_plus_header_bits():
    assert EmptyMaxBitsCb.max_total_bits() == EmptyMaxBitsCb.max_payload_bits() + HEADER_BITS


def test_max_bits_are_identical_across_different_subclasses():
    assert EmptyMaxBitsCb.max_payload_bits() == FieldMaxBitsCb.max_payload_bits()
    assert EmptyMaxBitsCb.max_total_bits() == FieldMaxBitsCb.max_total_bits()


def test_max_bits_return_int():
    assert isinstance(EmptyMaxBitsCb.max_payload_bits(), int)
    assert isinstance(EmptyMaxBitsCb.max_total_bits(), int)
