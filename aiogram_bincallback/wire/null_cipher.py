from aiogram_bincallback.wire.cipher import ICipher


class NullCipher(ICipher):
    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data
