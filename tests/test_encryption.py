import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import DecodeError
from aiogram_bincallback import DecryptionError
from aiogram_bincallback import bfield
from aiogram_bincallback import configure
from aiogram_bincallback.core import CipherReconfiguredAfterUseError
from aiogram_bincallback.wire import Base128WireCodec
from aiogram_bincallback.wire import ICipher
from aiogram_bincallback.wire import NullCipher
from tests.conftest import reset_configuration


class XorCipher(ICipher):
    def __init__(self, key: bytes) -> None:
        self._key = key

    def encrypt(self, data: bytes) -> bytes:
        return self._apply(data)

    def decrypt(self, data: bytes) -> bytes:
        return self._apply(data)

    def _apply(self, data: bytes) -> bytes:
        return bytes(byte ^ self._key[index % len(self._key)] for index, byte in enumerate(data))


class RejectingCipher(ICipher):
    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        raise DecryptionError("key does not match")


class BrokenThirdPartyCipher(ICipher):
    def encrypt(self, data: bytes) -> bytes:
        return data

    def decrypt(self, data: bytes) -> bytes:
        raise RuntimeError("boom")


@pytest.fixture(autouse=True)
def restore_default_configuration():
    yield
    reset_configuration()


def test_pack_unpack_roundtrips_with_cipher_configured():
    configure(cipher=XorCipher(key=b"secret"))

    class EncryptedCb(BinaryCallbackData, prefix=5001, version=1):
        value: int = bfield(bits=8, signed=False)

    original = EncryptedCb(value=42)

    restored = EncryptedCb.unpack(original.pack())

    assert restored == original


def test_packed_output_differs_between_null_cipher_and_real_cipher():
    class PlainCb(BinaryCallbackData, prefix=5002, version=1):
        value: int = bfield(bits=8, signed=False)

    plain_packed = PlainCb(value=7).pack()

    reset_configuration()
    configure(cipher=XorCipher(key=b"secret"))
    encrypted_packed = PlainCb(value=7).pack()

    assert plain_packed != encrypted_packed


def test_get_header_still_works_when_cipher_is_configured():
    configure(cipher=XorCipher(key=b"secret"))

    class HeaderCb(BinaryCallbackData, prefix=5003, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = HeaderCb(value=1).pack()

    header = HeaderCb.get_header(packed)

    assert header is not None
    assert header.prefix == 5003
    assert header.version == 1


def test_is_valid_still_works_when_cipher_is_configured():
    configure(cipher=XorCipher(key=b"secret"))

    class ValidCb(BinaryCallbackData, prefix=5004, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = ValidCb(value=1).pack()

    assert ValidCb.is_valid(packed) is True


def test_unpack_with_mismatched_key_does_not_silently_return_original_value():
    configure(cipher=XorCipher(key=b"secret"))

    class MismatchedKeyCb(BinaryCallbackData, prefix=5005, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = MismatchedKeyCb(value=1).pack()

    reset_configuration()
    configure(cipher=XorCipher(key=b"other-key"))

    try:
        restored = MismatchedKeyCb.unpack(packed)
    except DecodeError:
        return

    assert restored.value != 1


def test_unpack_wraps_decryption_error_as_decode_error():
    class RejectedCb(BinaryCallbackData, prefix=5006, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = RejectedCb(value=1).pack()

    reset_configuration()
    configure(cipher=RejectingCipher())

    with pytest.raises(DecodeError):
        RejectedCb.unpack(packed)


def test_get_header_returns_none_when_third_party_cipher_raises_arbitrary_error():
    class BrokenCb(BinaryCallbackData, prefix=5007, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = BrokenCb(value=1).pack()

    reset_configuration()
    configure(cipher=BrokenThirdPartyCipher())

    assert BrokenCb.get_header(packed) is None


def test_is_valid_returns_false_when_third_party_cipher_raises_arbitrary_error():
    class BrokenValidCb(BinaryCallbackData, prefix=5008, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = BrokenValidCb(value=1).pack()

    reset_configuration()
    configure(cipher=BrokenThirdPartyCipher())

    assert BrokenValidCb.is_valid(packed) is False


def test_null_cipher_is_transparent_by_default_without_any_configuration():
    class DefaultCb(BinaryCallbackData, prefix=5009, version=1):
        value: int = bfield(bits=8, signed=False)

    original = DefaultCb(value=13)

    restored = DefaultCb.unpack(original.pack())

    assert restored == original


def test_cipher_applies_to_every_binary_callback_data_subclass_at_once():
    configure(cipher=XorCipher(key=b"shared"))

    class FirstCb(BinaryCallbackData, prefix=5010, version=1):
        value: int = bfield(bits=8, signed=False)

    class SecondCb(BinaryCallbackData, prefix=5011, version=1):
        value: int = bfield(bits=8, signed=False)

    first_restored = FirstCb.unpack(FirstCb(value=1).pack())
    second_restored = SecondCb.unpack(SecondCb(value=2).pack())

    assert first_restored.value == 1
    assert second_restored.value == 2


def test_configuring_wire_codec_alongside_cipher_still_roundtrips():
    configure(wire_codec=Base128WireCodec(), cipher=XorCipher(key=b"combo"))

    class ComboCb(BinaryCallbackData, prefix=5012, version=1):
        value: int = bfield(bits=16, signed=False)

    original = ComboCb(value=4242)

    restored = ComboCb.unpack(original.pack())

    assert restored == original


def test_reconfiguring_cipher_after_pack_raises():
    configure(cipher=XorCipher(key=b"secret"))

    class UsedCb(BinaryCallbackData, prefix=5013, version=1):
        value: int = bfield(bits=8, signed=False)

    UsedCb(value=1).pack()

    with pytest.raises(CipherReconfiguredAfterUseError):
        configure(cipher=NullCipher())


def test_reconfiguring_cipher_after_unpack_raises():
    configure(cipher=XorCipher(key=b"secret"))

    class UsedOnUnpackCb(BinaryCallbackData, prefix=5014, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = UsedOnUnpackCb(value=1).pack()
    UsedOnUnpackCb.unpack(packed)

    with pytest.raises(CipherReconfiguredAfterUseError):
        configure(cipher=NullCipher())


def test_reconfiguring_wire_codec_only_after_cipher_use_does_not_raise():
    configure(cipher=XorCipher(key=b"secret"))

    class UsedThenWireCodecCb(BinaryCallbackData, prefix=5015, version=1):
        value: int = bfield(bits=8, signed=False)

    UsedThenWireCodecCb(value=1).pack()

    configure(wire_codec=Base128WireCodec())
