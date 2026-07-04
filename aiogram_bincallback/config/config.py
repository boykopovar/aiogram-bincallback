from typing import Optional

from aiogram_bincallback.wire.base128_codec import Base128WireCodec
from aiogram_bincallback.wire.cipher import ICipher
from aiogram_bincallback.wire.null_cipher import NullCipher
from aiogram_bincallback.wire.protocol import IWireCodec

_wire_codec: IWireCodec = Base128WireCodec()
_cipher: ICipher = NullCipher()


def configure(
    *,
    wire_codec: Optional[IWireCodec] = None,
    cipher: Optional[ICipher] = None,
) -> None:
    global _wire_codec
    global _cipher
    if wire_codec is not None:
        _wire_codec = wire_codec
    if cipher is not None:
        _cipher = cipher


def get_wire_codec() -> IWireCodec:
    return _wire_codec


def get_cipher() -> ICipher:
    return _cipher
