from typing import Protocol


class WireCodec(Protocol):
    def encode(self, data: bytes) -> str:
        ...

    def decode(self, packed: str) -> bytes:
        ...
