from aiogram_bincallback.wire import ICipher
from aiogram_bincallback.wire import NullCipher


def test_null_cipher_is_an_icipher():
    assert isinstance(NullCipher(), ICipher)


def test_null_cipher_encrypt_returns_data_unchanged():
    cipher = NullCipher()
    data = b"\x01\x02\x03"

    assert cipher.encrypt(data) == data


def test_null_cipher_decrypt_returns_data_unchanged():
    cipher = NullCipher()
    data = b"\x01\x02\x03"

    assert cipher.decrypt(data) == data


def test_null_cipher_roundtrips_empty_bytes():
    cipher = NullCipher()

    assert cipher.decrypt(cipher.encrypt(b"")) == b""


def test_null_cipher_roundtrips_arbitrary_bytes():
    cipher = NullCipher()
    data = bytes(range(256))

    assert cipher.decrypt(cipher.encrypt(data)) == data
