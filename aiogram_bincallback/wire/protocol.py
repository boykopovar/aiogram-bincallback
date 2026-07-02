from abc import ABC
from abc import abstractmethod


class IWireCodec(ABC):
    @abstractmethod
    def encode(self, data: bytes) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode(self, packed: str) -> bytes:
        raise NotImplementedError
