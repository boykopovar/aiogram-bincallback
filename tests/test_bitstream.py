from aiogram_bincallback.bitstream import BitReader
from aiogram_bincallback.bitstream import BitWriter


def test_writer_then_reader_roundtrips_single_value():
    writer = BitWriter()
    writer.write_uint(5, 3)

    reader = BitReader(writer.to_bytes())
    value = reader.read_uint(3)

    assert value == 5


def test_writer_then_reader_roundtrips_sequence_of_values_in_order():
    writer = BitWriter()
    writer.write_uint(1, 1)
    writer.write_uint(42, 8)
    writer.write_uint(0, 4)
    writer.write_uint(7, 3)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(1) == 1
    assert reader.read_uint(8) == 42
    assert reader.read_uint(4) == 0
    assert reader.read_uint(3) == 7


def test_write_zero_bits_does_not_advance_stream():
    writer = BitWriter()
    writer.write_uint(0, 0)
    writer.write_uint(9, 4)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(4) == 9


def test_write_zero_value_with_zero_bits_is_a_no_op():
    writer = BitWriter()
    writer.write_uint(0, 0)

    assert writer.to_bytes() == b""


def test_writer_output_length_matches_bit_count_rounded_up_to_bytes():
    writer = BitWriter()
    writer.write_uint(1, 1)

    assert len(writer.to_bytes()) == 1


def test_writer_pads_partial_final_byte_with_zero_bits():
    writer = BitWriter()
    writer.write_uint(1, 1)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(1) == 1
    assert reader.read_uint(7) == 0


def test_writer_spans_multiple_bytes_for_wide_values():
    writer = BitWriter()
    writer.write_uint(0b1_1111_1111, 9)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(9) == 0b1_1111_1111


def test_reader_can_start_at_nonzero_bit_offset():
    writer = BitWriter()
    writer.write_uint(0, 8)
    writer.write_uint(123, 8)

    reader = BitReader(writer.to_bytes(), start_bit=8)

    assert reader.read_uint(8) == 123


def test_reader_tracks_bit_position_after_each_read():
    writer = BitWriter()
    writer.write_uint(3, 2)
    writer.write_uint(5, 3)

    reader = BitReader(writer.to_bytes())
    reader.read_uint(2)

    assert reader.position_bits == 2
    reader.read_uint(3)
    assert reader.position_bits == 5


def test_maximum_value_for_given_bit_width_roundtrips():
    writer = BitWriter()
    max_value_for_5_bits = (1 << 5) - 1
    writer.write_uint(max_value_for_5_bits, 5)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(5) == max_value_for_5_bits


def test_zero_value_roundtrips_for_any_bit_width():
    writer = BitWriter()
    writer.write_uint(0, 16)

    reader = BitReader(writer.to_bytes())

    assert reader.read_uint(16) == 0


def test_multiple_writers_produce_independent_buffers():
    first = BitWriter()
    first.write_uint(1, 4)
    second = BitWriter()
    second.write_uint(2, 4)

    assert first.to_bytes() != second.to_bytes()


def test_bit_position_starts_at_zero_by_default():
    writer = BitWriter()
    writer.write_uint(1, 8)

    reader = BitReader(writer.to_bytes())

    assert reader.position_bits == 0


def test_signed_negative_value_roundtrips():
    writer = BitWriter()
    writer.write_int(-1, 4)

    reader = BitReader(writer.to_bytes())

    assert reader.read_int(4) == -1


def test_signed_positive_value_roundtrips():
    writer = BitWriter()
    writer.write_int(5, 4)

    reader = BitReader(writer.to_bytes())

    assert reader.read_int(4) == 5
