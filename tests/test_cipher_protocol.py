import pytest

from aiogram_bincallback.wire import ICipher


def test_icipher_cannot_be_instantiated_directly():
    with pytest.raises(TypeError):
        ICipher()


def test_icipher_subclass_missing_encrypt_cannot_be_instantiated():
    class MissingEncrypt(ICipher):
        def decrypt(self, data: bytes) -> bytes:
            return data

    with pytest.raises(TypeError):
        MissingEncrypt()


def test_icipher_subclass_missing_decrypt_cannot_be_instantiated():
    class MissingDecrypt(ICipher):
        def encrypt(self, data: bytes) -> bytes:
            return data

    with pytest.raises(TypeError):
        MissingDecrypt()


def test_icipher_subclass_implementing_both_methods_can_be_instantiated():
    class CompleteCipher(ICipher):
        def encrypt(self, data: bytes) -> bytes:
            return data[::-1]

        def decrypt(self, data: bytes) -> bytes:
            return data[::-1]

    assert isinstance(CompleteCipher(), ICipher)
