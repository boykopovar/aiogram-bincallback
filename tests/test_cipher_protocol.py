import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import bfield
from aiogram_bincallback import configure
from aiogram_bincallback.core import CipherReconfiguredAfterUseError
from aiogram_bincallback.wire import ICipher
from tests.conftest import reset_configuration


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


class ReverseCipher(ICipher):
    def encrypt(self, data: bytes) -> bytes:
        return data[::-1]

    def decrypt(self, data: bytes) -> bytes:
        return data[::-1]


@pytest.fixture(autouse=True)
def _restore_default_config():
    yield
    reset_configuration()


class NoFieldModel(BinaryCallbackData, prefix=1, version=1):
    pass


class IntFieldModel(BinaryCallbackData, prefix=2, version=1):
    item_id: int = bfield(bits=32, signed=False)


class MultiFieldModel(BinaryCallbackData, prefix=3, version=1):
    a: int = bfield(bits=8, signed=False)
    b: int = bfield(bits=16, signed=False)
    flag: bool = bfield()


def test_reverse_cipher_roundtrip_no_fields():
    configure(cipher=ReverseCipher())

    packed = NoFieldModel().pack()
    unpacked = NoFieldModel.unpack(packed)

    assert isinstance(unpacked, NoFieldModel)
    assert NoFieldModel.is_valid(packed)


def test_reverse_cipher_roundtrip_int_field_sweep():
    configure(cipher=ReverseCipher())

    failures = []
    for value in (0, 1, 127, 128, 255, 256, 65535, 65536, 2**31, 2**32 - 1):
        packed = IntFieldModel(item_id=value).pack()
        try:
            unpacked = IntFieldModel.unpack(packed)
        except Exception as error:  # noqa: BLE001
            failures.append((value, repr(error)))
            continue
        if unpacked.item_id != value:
            failures.append((value, f"mismatch: got {unpacked.item_id}"))

    assert not failures, f"reverse cipher roundtrip failed for: {failures}"


def test_reverse_cipher_roundtrip_multi_field():
    configure(cipher=ReverseCipher())

    instance = MultiFieldModel(a=0, b=0, flag=False)
    packed = instance.pack()
    unpacked = MultiFieldModel.unpack(packed)

    assert unpacked.a == instance.a
    assert unpacked.b == instance.b
    assert unpacked.flag == instance.flag


def test_reverse_cipher_try_unpack_matches_expected_type():
    configure(cipher=ReverseCipher())

    packed = IntFieldModel(item_id=42).pack()
    result = BinaryCallbackData.try_unpack(packed, expected=IntFieldModel)

    assert result is not None
    assert result.item_id == 42


def test_packed_with_one_cipher_is_rejected_by_another_cipher():
    reset_configuration()
    packed_with_null = IntFieldModel(item_id=7).pack()

    reset_configuration()
    configure(cipher=ReverseCipher())
    unpacked = IntFieldModel.try_unpack(packed_with_null, expected=IntFieldModel)

    assert unpacked is None or unpacked.item_id != 7


def test_module_level_pack_before_configure_raises_instead_of_baking_in_wrong_cipher():
    reset_configuration()

    BAKED_IN_BUTTON_CALLBACK_DATA = IntFieldModel(item_id=42).pack()

    with pytest.raises(CipherReconfiguredAfterUseError):
        configure(cipher=ReverseCipher())

    assert BAKED_IN_BUTTON_CALLBACK_DATA == IntFieldModel(item_id=42).pack()
