import pytest

from aiogram_bincallback.core import MAX_CALLBACK_LENGTH
from aiogram_bincallback.core import PayloadCorruptError
from aiogram_bincallback.wire import Base128WireCodec
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS
from aiogram_bincallback.wire.constants import BASE128_ALPHABET
from aiogram_bincallback.wire.constants import BASE128_RADIX
from aiogram_bincallback.wire.constants import MAX_TOTAL_BITS


def test_base128_alphabet_has_exactly_128_characters():
    assert len(BASE128_ALPHABET) == BASE128_RADIX == 128


def test_base128_alphabet_covers_every_ascii_code_point_once():
    assert BASE128_ALPHABET == "".join(chr(code) for code in range(128))


def test_base128_alphabet_has_no_duplicate_characters():
    assert len(set(BASE128_ALPHABET)) == len(BASE128_ALPHABET)


def test_max_total_bits_is_the_largest_byte_aligned_size_that_always_fits():
    assert MAX_TOTAL_BITS == 440


def test_max_payload_bits_is_max_total_bits_minus_header_bits():
    from aiogram_bincallback.core import HEADER_BITS

    assert MAX_PAYLOAD_BITS == MAX_TOTAL_BITS - HEADER_BITS
    assert MAX_PAYLOAD_BITS == 416


def test_worst_case_data_at_max_total_bits_always_fits_in_callback_length():
    codec = Base128WireCodec()
    data = b"\xff" * (MAX_TOTAL_BITS // 8)

    packed = codec.encode(data)

    assert len(packed) <= MAX_CALLBACK_LENGTH
    assert codec.decode(packed) == data


def test_worst_case_data_one_byte_above_max_total_bits_can_exceed_callback_length():
    codec = Base128WireCodec()
    data = b"\xff" * (MAX_TOTAL_BITS // 8 + 1)

    packed = codec.encode(data)

    assert len(packed) > MAX_CALLBACK_LENGTH


def test_encode_empty_bytes_roundtrips():
    codec = Base128WireCodec()

    packed = codec.encode(b"")

    assert codec.decode(packed) == b""


def test_encode_decode_roundtrips_arbitrary_bytes():
    codec = Base128WireCodec()
    data = bytes([0x01, 0x02, 0x03, 0xFF, 0x00, 0x7F])

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_preserves_leading_zero_bytes():
    codec = Base128WireCodec()
    data = b"\x00\x00\x01"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_all_zero_bytes_roundtrips():
    codec = Base128WireCodec()
    data = b"\x00\x00\x00\x00"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_all_ff_bytes_roundtrips():
    codec = Base128WireCodec()
    data = b"\xff\xff\xff\xff"

    packed = codec.encode(data)

    assert codec.decode(packed) == data


def test_encode_single_byte_roundtrips_for_every_value():
    codec = Base128WireCodec()

    for byte_value in (0, 1, 127, 128, 254, 255):
        data = bytes([byte_value])
        packed = codec.encode(data)
        assert codec.decode(packed) == data


def test_encode_returns_string_made_only_of_alphabet_characters():
    codec = Base128WireCodec()
    data = bytes(range(32))

    packed = codec.encode(data)

    assert all(character in BASE128_ALPHABET for character in packed)


def test_encode_output_stays_within_ascii_range():
    codec = Base128WireCodec()
    data = bytes(range(64))

    packed = codec.encode(data)

    assert all(ord(character) < 128 for character in packed)


def test_decode_rejects_character_outside_alphabet():
    codec = Base128WireCodec()

    with pytest.raises(PayloadCorruptError):
        codec.decode("ab" + chr(128) + "cd")


def test_decode_empty_string_raises_payload_corrupt_error():
    codec = Base128WireCodec()

    with pytest.raises(PayloadCorruptError):
        codec.decode("")


def test_decode_garbage_with_corrupt_marker_bits_raises_overflow_error():
    codec = Base128WireCodec()

    with pytest.raises(OverflowError):
        codec.decode(chr(127) * 4)


def test_larger_payloads_encode_to_more_characters_than_smaller_ones():
    codec = Base128WireCodec()

    short_packed = codec.encode(b"\x01")
    long_packed = codec.encode(b"\x01" * 32)

    assert len(long_packed) > len(short_packed)
