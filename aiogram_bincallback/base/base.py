from enum import Enum
from typing import Optional
from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from pydantic import Field
from pydantic.fields import FieldInfo

from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_SIGNED_KEY
from aiogram_bincallback.core import BinaryCallbackError
from aiogram_bincallback.core import DecodeError
from aiogram_bincallback.core import PrefixMismatchError
from aiogram_bincallback.core import VersionMismatchError
from aiogram_bincallback.header import check_size_limit
from aiogram_bincallback.header import decode_header
from aiogram_bincallback.header import encode_header
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.registry import make_aiogram_prefix
from aiogram_bincallback.registry import register
from aiogram_bincallback.wire import Base64WireCodec
from aiogram_bincallback.wire import WireCodec

_DEFAULT_WIRE_CODEC: WireCodec = Base64WireCodec()


def bfield(
    *,
    bits: Optional[int] = None,
    bin_order: Optional[Sequence[Enum]] = None,
    signed: Optional[bool] = None,
    **kw: object,
) -> FieldInfo:
    ...


class BinaryCallbackData(CallbackData, prefix="_bin_"):
    def __init_subclass__(
        cls,
        prefix: Optional[int] = None,
        version: int = 1,
        wire_codec: WireCodec = _DEFAULT_WIRE_CODEC,
        **kw: object,
    ) -> None:
        ...

    def pack(self) -> str:
        ...

    @classmethod
    def unpack(cls, packed: str) -> "BinaryCallbackData":
        ...
