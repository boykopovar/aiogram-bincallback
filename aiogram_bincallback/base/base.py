from enum import Enum
from typing import Any
from typing import Dict
from typing import Optional
from typing import Sequence

from aiogram.filters.callback_data import CallbackData
from pydantic import Field
from pydantic.fields import FieldInfo

from aiogram_bincallback.codec import decode_fields
from aiogram_bincallback.codec import encode_fields
from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_SIGNED_KEY
from aiogram_bincallback.core import BinaryCallbackError
from aiogram_bincallback.core import DecodeError
from aiogram_bincallback.core import HEADER_BITS
from aiogram_bincallback.core import PrefixMismatchError
from aiogram_bincallback.core import VersionMismatchError
from aiogram_bincallback.header import check_size_limit
from aiogram_bincallback.header import decode_header
from aiogram_bincallback.header import encode_header
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.registry import make_aiogram_prefix
from aiogram_bincallback.registry import register
from aiogram_bincallback.wire import Base93WireCodec
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS
from aiogram_bincallback.wire import WireCodec

_WIRE_CODEC: WireCodec = Base93WireCodec()


def bfield(
    *,
    bits: Optional[int] = None,
    bin_order: Optional[Sequence[Enum]] = None,
    signed: Optional[bool] = None,
    **kw: object,
) -> FieldInfo:
    extra = kw.pop("json_schema_extra", {}) or {}
    extra[BIN_BITS_KEY] = bits
    extra[BIN_ORDER_KEY] = bin_order
    extra[BIN_SIGNED_KEY] = signed
    return Field(json_schema_extra=extra, **kw)


class BinaryCallbackData(CallbackData, prefix="_bin_"):
    __bin_prefix__: Optional[int] = None
    __bin_version__: int = 1

    def __init_subclass__(
        cls,
        prefix: Optional[int] = None,
        version: int = 1,
        **kw: object,
    ) -> None:
        super().__init_subclass__(prefix=make_aiogram_prefix(prefix), **kw)
        cls.__bin_prefix__ = prefix
        cls.__bin_version__ = version

    @classmethod
    def __pydantic_init_subclass__(cls, **kw: object) -> None:
        super().__pydantic_init_subclass__(**kw)
        if cls is BinaryCallbackData:
            return
        if cls.__bin_prefix__ is not None:
            register(cls.__bin_prefix__, cls.__bin_version__, cls)
        cls.__bin_plan__ = build_codec_plan(cls)
        check_size_limit(cls.__bin_plan__, MAX_PAYLOAD_BITS)

    def pack(self) -> str:
        header = encode_header(self.__bin_prefix__, self.__bin_version__)
        payload = encode_fields(self.__bin_plan__, self)
        return _WIRE_CODEC.encode(header + payload)

    @classmethod
    def unpack(cls, packed: str) -> "BinaryCallbackData":
        try:
            raw = _WIRE_CODEC.decode(packed)
            prefix, version = decode_header(raw)
            if prefix != cls.__bin_prefix__:
                raise PrefixMismatchError(prefix, cls.__bin_prefix__)
            if version != cls.__bin_version__:
                raise VersionMismatchError(version, cls.__bin_version__)
            data: Dict[str, Any]
            data, _ = decode_fields(cls.__bin_plan__, raw, HEADER_BITS)
            return cls(**data)
        except BinaryCallbackError:
            raise
        except Exception as error:
            raise DecodeError(str(error)) from error
