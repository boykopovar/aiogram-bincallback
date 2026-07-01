class BitWriter:
    def __init__(self) -> None:
        ...

    def write_uint(self, value: int, bits: int) -> None:
        ...

    def write_int(self, value: int, bits: int) -> None:
        ...

    def to_bytes(self) -> bytes:
        ...


class BitReader:
    def __init__(self, data: bytes, start_bit: int = 0) -> None:
        ...

    def read_uint(self, bits: int) -> int:
        ...

    def read_int(self, bits: int) -> int:
        ...

    @property
    def position_bits(self) -> int:
        ...
