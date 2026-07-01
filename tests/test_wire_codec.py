import pytest

from aiogram_bincallback.core import MAX_CALLBACK_LENGTH
from aiogram_bincallback.core import PayloadCorruptError
from aiogram_bincallback.wire import Base93WireCodec
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS
from aiogram_bincallback.wire.constants import BASE93_ALPHABET
from aiogram_bincallback.wire.constants import BASE93_RADIX
from aiogram_bincallback.wire.constants import MAX_TOTAL_BITS


def test_base93_alphabet_has_exactly_93_characters():
    assert len(BASE93_ALPHABET) == BASE93_RADIX == 93


def test_base93_alphabet_excludes_json_escaped_characters():
    assert '"' not in BASE93_ALPHABET
    assert "\\" not in BASE93_ALPHABET


def test_base93_alphabet_has_no_duplicate_characters():
    assert len(set(BASE93_ALPHABET)) == len(BASE93_ALPHABET)


def test_max_total_bits_matches_93_pow_64_bit_length_minus_one():
    assert MAX_TOTAL_BITS == (BASE93_RADIX ** MAX_CALLBACK_LENGTH).bit_length() - 1
    assert MAX_TOTAL_BITS == 418


def test_max_payload_bits_is_max_total_bits_minus_header_bits():
    from aiogram_bincallback.core import HEADER_BITS

    assert MAX_PAYLOAD_BITS == MAX_TOTAL_BITS - HEADER_BITS
    assert MAX_PAYLOAD_BITS == 394


def test_encode_empty_bytes_roundtrips():
    codec = Base93WireCodec()

    packed = codec.encode(b"")

    assert codec.decode(packed) == b""


def test_encode_decode_roundtrips_arbitrary_bytes():
    codec = Base93WireCodec()
    data = bytes([0x01, 0x02, 0x03, 0xFF, 0x00, 0x7F])

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_preserves_leading_zero_bytes():
    codec = Base93WireCodec()
    data = b"\x00\x00\x01"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_all_zero_bytes_roundtrips():
    codec = Base93WireCodec()
    data = b"\x00\x00\x00\x00"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_all_ff_bytes_roundtrips():
    codec = Base93WireCodec()
    data = b"\xff\xff\xff\xff"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_single_byte_roundtrips_for_every_value():
    codec = Base93WireCodec()

    for byte_value in (0, 1, 127, 128, 254, 255):
        data = bytes([byte_value])
        packed = codec.encode(data)
        assert codec.decode(packed) == data


def test_encode_returns_string_made_only_of_alphabet_characters():
    codec = Base93WireCodec()
    data = bytes(range(32))

    packed = codec.encode(data)

    assert all(character in BASE93_ALPHABET for character in packed)


def test_encode_output_contains_no_quote_or_backslash():
    codec = Base93WireCodec()
    data = bytes(range(64))

    packed = codec.encode(data)

    assert '"' not in packed
    assert "\\" not in packed


def test_decode_rejects_character_outside_alphabet():
    codec = Base93WireCodec()

    with pytest.raises(PayloadCorruptError):
        codec.decode('ab"cd')


def test_decode_rejects_backslash_character():
    codec = Base93WireCodec()

    with pytest.raises(PayloadCorruptError):
        codec.decode("ab\\cd")


def test_decode_empty_string_raises_payload_corrupt_error():
    codec = Base93WireCodec()

    with pytest.raises(PayloadCorruptError):
        codec.decode("")


def test_decode_garbage_with_corrupt_marker_bits_raises_overflow_error():
    codec = Base93WireCodec()

    with pytest.raises(OverflowError):
        codec.decode("zzzz")


def test_larger_payloads_encode_to_more_characters_than_smaller_ones():
    codec = Base93WireCodec()

    short_packed = codec.encode(b"\x01")
    long_packed = codec.encode(b"\x01" * 32)

    assert len(long_packed) > len(short_packed)
