from abc import ABC
from abc import abstractmethod


class ICipher(ABC):
    @abstractmethod
    def encrypt(self, data: bytes) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def decrypt(self, data: bytes) -> bytes:
        raise NotImplementedError
