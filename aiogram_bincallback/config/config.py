from typing import Optional

from aiogram_bincallback.core.exceptions import CipherReconfiguredAfterUseError
from aiogram_bincallback.wire.base128_codec import Base128WireCodec
from aiogram_bincallback.wire.cipher import ICipher
from aiogram_bincallback.wire.null_cipher import NullCipher
from aiogram_bincallback.wire.protocol import IWireCodec

_wire_codec: IWireCodec = Base128WireCodec()
_cipher: ICipher = NullCipher()
_cipher_used: bool = False


def configure(
    *,
    wire_codec: Optional[IWireCodec] = None,
    cipher: Optional[ICipher] = None,
) -> None:
    global _wire_codec
    global _cipher
    global _cipher_used
    if wire_codec is not None:
        _wire_codec = wire_codec
    if cipher is not None:
        if _cipher_used and cipher is not _cipher:
            raise CipherReconfiguredAfterUseError()
        _cipher = cipher
        _cipher_used = False


def get_wire_codec() -> IWireCodec:
    return _wire_codec


def get_cipher() -> ICipher:
    global _cipher_used
    _cipher_used = True
    return _cipher
