import pytest

from aiogram_bincallback.config import configure
from aiogram_bincallback.config import get_cipher
from aiogram_bincallback.config import get_wire_codec
from aiogram_bincallback.core import CipherReconfiguredAfterUseError
from aiogram_bincallback.wire import Base128WireCodec
from aiogram_bincallback.wire import ICipher
from aiogram_bincallback.wire import IWireCodec
from aiogram_bincallback.wire import NullCipher
from tests.conftest import reset_configuration


class UppercaseCipher(ICipher):
    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        return data


class ReversingWireCodec(IWireCodec):
    def encode(self, data: bytes) -> str:
        return data.hex()[::-1]

    def decode(self, packed: str) -> bytes:
        return bytes.fromhex(packed[::-1])


@pytest.fixture(autouse=True)
def restore_default_configuration():
    yield
    reset_configuration()


def test_default_cipher_is_null_cipher():
    assert isinstance(get_cipher(), NullCipher)


def test_default_wire_codec_is_base128_wire_codec():
    assert isinstance(get_wire_codec(), Base128WireCodec)


def test_configure_replaces_cipher():
    cipher = UppercaseCipher()

    configure(cipher=cipher)

    assert get_cipher() is cipher


def test_configure_replaces_wire_codec():
    wire_codec = ReversingWireCodec()

    configure(wire_codec=wire_codec)

    assert get_wire_codec() is wire_codec


def test_configure_with_no_arguments_leaves_current_configuration_untouched():
    cipher = UppercaseCipher()
    wire_codec = ReversingWireCodec()
    configure(cipher=cipher, wire_codec=wire_codec)

    configure()

    assert get_cipher() is cipher
    assert get_wire_codec() is wire_codec


def test_configure_can_replace_only_cipher_and_keep_wire_codec():
    wire_codec = ReversingWireCodec()
    configure(wire_codec=wire_codec, cipher=NullCipher())

    configure(cipher=UppercaseCipher())

    assert get_wire_codec() is wire_codec
    assert isinstance(get_cipher(), UppercaseCipher)


def test_configure_can_replace_only_wire_codec_and_keep_cipher():
    cipher = UppercaseCipher()
    configure(wire_codec=Base128WireCodec(), cipher=cipher)

    configure(wire_codec=ReversingWireCodec())

    assert get_cipher() is cipher
    assert isinstance(get_wire_codec(), ReversingWireCodec)


def test_configure_cipher_before_any_use_does_not_raise():
    configure(cipher=UppercaseCipher())
    configure(cipher=NullCipher())

    assert isinstance(get_cipher(), NullCipher)


def test_configure_cipher_after_use_raises():
    configure(cipher=UppercaseCipher())
    get_cipher()

    with pytest.raises(CipherReconfiguredAfterUseError):
        configure(cipher=NullCipher())


def test_configure_wire_codec_after_cipher_use_does_not_raise():
    configure(cipher=UppercaseCipher())
    get_cipher()

    configure(wire_codec=ReversingWireCodec())

    assert isinstance(get_wire_codec(), ReversingWireCodec)


def test_configure_cipher_after_use_leaves_previous_cipher_active():
    cipher = UppercaseCipher()
    configure(cipher=cipher)
    get_cipher()

    with pytest.raises(CipherReconfiguredAfterUseError):
        configure(cipher=NullCipher())

    assert get_cipher() is cipher
