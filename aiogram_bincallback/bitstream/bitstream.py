class BitWriter:
    def __init__(self) -> None:
        self._accumulator = 0
        self._length_bits = 0

    def write_uint(self, value: int, bits: int) -> None:
        self._accumulator = (self._accumulator << bits) | (value & _bit_mask(bits))
        self._length_bits += bits

    def write_int(self, value: int, bits: int) -> None:
        self.write_uint(_signed_to_unsigned(value, bits), bits)

    def to_bytes(self) -> bytes:
        padding_bits = -self._length_bits % 8
        padded_value = self._accumulator << padding_bits
        padded_length_bits = self._length_bits + padding_bits
        return padded_value.to_bytes(padded_length_bits // 8, byteorder="big")


class BitReader:
    def __init__(self, data: bytes, start_bit: int = 0) -> None:
        self._value = int.from_bytes(data, byteorder="big")
        self._total_bits = len(data) * 8
        self._position_bits = start_bit

    def read_uint(self, bits: int) -> int:
        remaining_bits = self._total_bits - self._position_bits - bits
        result = (self._value >> remaining_bits) & _bit_mask(bits)
        self._position_bits += bits
        return result

    def read_int(self, bits: int) -> int:
        return _unsigned_to_signed(self.read_uint(bits), bits)

    @property
    def position_bits(self) -> int:
        return self._position_bits


def _bit_mask(bits: int) -> int:
    return (1 << bits) - 1


def _signed_to_unsigned(value: int, bits: int) -> int:
    return value & _bit_mask(bits)


def _unsigned_to_signed(value: int, bits: int) -> int:
    sign_bit = 1 << (bits - 1)
    return value - (1 << bits) if value & sign_bit else value
