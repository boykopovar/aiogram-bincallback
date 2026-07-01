from aiogram_bincallback.core.exceptions import PayloadCorruptError
from aiogram_bincallback.wire.constants import BASE93_ALPHABET
from aiogram_bincallback.wire.constants import BASE93_RADIX

_LENGTH_MARKER_BIT_COUNT = 8


class Base93WireCodec:
    def encode(self, data: bytes) -> str:
        marker = 1 << (len(data) * _LENGTH_MARKER_BIT_COUNT)
        value = marker | self._bytes_to_int(data)
        digits = []
        while value > 0:
            value, remainder = divmod(value, BASE93_RADIX)
            digits.append(BASE93_ALPHABET[remainder])
        if not digits:
            digits.append(BASE93_ALPHABET[0])
        return "".join(reversed(digits))

    def decode(self, packed: str) -> bytes:
        value = 0
        for character in packed:
            digit = BASE93_ALPHABET.find(character)
            if digit < 0:
                raise PayloadCorruptError(f"character {character!r} is outside the base93 alphabet")
            value = value * BASE93_RADIX + digit
        marker_bit_length = value.bit_length()
        if marker_bit_length == 0:
            raise PayloadCorruptError("payload is missing its length marker bit")
        length_bits = (marker_bit_length - 1) - ((marker_bit_length - 1) % _LENGTH_MARKER_BIT_COUNT)
        length_bytes = length_bits // _LENGTH_MARKER_BIT_COUNT
        marker = 1 << (length_bytes * _LENGTH_MARKER_BIT_COUNT)
        if value < marker or value >= marker << _LENGTH_MARKER_BIT_COUNT:
            raise PayloadCorruptError("payload length marker bit is corrupt")
        return self._int_to_bytes(value - marker, length_bytes)

    def _bytes_to_int(self, data: bytes) -> int:
        return int.from_bytes(data, byteorder="big")

    def _int_to_bytes(self, value: int, length: int) -> bytes:
        return value.to_bytes(length, byteorder="big")
