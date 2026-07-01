from aiogram_bincallback.wire.constants import BASE93_ALPHABET


class Base93WireCodec:
    def encode(self, data: bytes) -> str:
        ...

    def decode(self, packed: str) -> bytes:
        ...

    def _bytes_to_int(self, data: bytes) -> int:
        ...

    def _int_to_bytes(self, value: int, length: int) -> bytes:
        ...
