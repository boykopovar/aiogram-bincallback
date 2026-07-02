from typing import Protocol


class WireCodec(Protocol):
    def encode(self, data: bytes) -> str:  # pragma: no cover
        ...

    def decode(self, packed: str) -> bytes:  # pragma: no cover
        ...
