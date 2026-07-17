from enum import Enum
from typing import Callable, Union, ClassVar
from typing import cast
from typing import Dict
from typing import Optional
from typing import Sequence
from typing import Type
from typing import TypeVar
from typing import NamedTuple

from aiogram.filters.callback_data import CallbackData
from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic.json_schema import JsonDict
from pydantic_core import PydanticUndefined

from aiogram_bincallback.codec import decode_fields
from aiogram_bincallback.codec import describe_instance
from aiogram_bincallback.codec import encode_fields
from aiogram_bincallback.config import get_cipher
from aiogram_bincallback.config import get_wire_codec
from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_MAX_LEN_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_SIGNED_KEY
from aiogram_bincallback.core import BinaryCallbackError
from aiogram_bincallback.core import DecodeError
from aiogram_bincallback.core import ExpectedTypeError
from aiogram_bincallback.core import HEADER_BITS
from aiogram_bincallback.core import PrefixMismatchError
from aiogram_bincallback.core import VersionMismatchError
from aiogram_bincallback.header import check_size_limit
from aiogram_bincallback.header import decode_header
from aiogram_bincallback.header import encode_header
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import CodecPlan
from aiogram_bincallback.registry import make_aiogram_prefix, expand_expected_types
from aiogram_bincallback.registry import register
from aiogram_bincallback.registry import resolve
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS


PrefixEnumT = TypeVar("PrefixEnumT", bound=Enum)
BinaryCallbackDataT = TypeVar("BinaryCallbackDataT", bound="BinaryCallbackData")


class BinCbHeader(NamedTuple):
    prefix: int
    version: int


BinFieldExtra = Dict[str, object]


def bfield(
    *,
    bits: Optional[int] = None,
    bin_order: Optional[Sequence[Enum]] = None,
    signed: Optional[bool] = None,
    max_len: Optional[int] = None,
    default: object = PydanticUndefined,
    default_factory: Optional[Callable[[], object]] = None,
) -> FieldInfo:
    extra: BinFieldExtra = {
        BIN_BITS_KEY: bits,
        BIN_ORDER_KEY: bin_order,
        BIN_SIGNED_KEY: signed,
        BIN_MAX_LEN_KEY: max_len
    }
    schema_extra = cast(JsonDict, extra)
    if default_factory is not None:
        return cast(FieldInfo, Field(default_factory=default_factory, json_schema_extra=schema_extra))
    return cast(FieldInfo, Field(default=default, json_schema_extra=schema_extra))


class BinaryCallbackData(CallbackData, prefix="_bin_"):
    __bin_prefix__: Optional[int] = None
    __bin_version__: int = 1
    __bin_plan__: ClassVar[CodecPlan]

    def __init_subclass__(
        cls,
        prefix: int,
        version: int,
        **kw: object,
    ) -> None:
        if prefix is None:
            raise TypeError("prefix cannot be None")
        super().__init_subclass__(prefix=make_aiogram_prefix(prefix), **kw)
        cls.__bin_prefix__ = prefix
        cls.__bin_version__ = version

    @classmethod
    def get_header(cls, packed: str) -> Optional[BinCbHeader]:
        try:
            wire_codec = get_wire_codec()
            cipher = get_cipher()
            raw = cipher.decrypt(wire_codec.decode(packed))
            prefix, version = decode_header(raw)
        except Exception:
            return None

        return BinCbHeader(
            prefix=prefix,
            version=version,
        )

    @classmethod
    def is_valid(cls, packed: str) -> bool:
        if cls is BinaryCallbackData:
            raise TypeError("is_valid() must be called on a subclass")

        header = cls.get_header(packed)
        return (
            header is not None
            and header.prefix == cls.__bin_prefix__
            and header.version == cls.__bin_version__
        )

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
        assert self.__bin_prefix__ is not None
        header = encode_header(self.__bin_prefix__, self.__bin_version__)
        payload = encode_fields(self.__bin_plan__, self)
        raw = get_cipher().encrypt(header + payload)
        return get_wire_codec().encode(raw)

    def describe(
        self,
        prefix_enum: Optional[Type[PrefixEnumT]] = None,
        bool_as_int: bool = True,
        enum_as_name: bool = True,
    ) -> str:
        if self.__bin_prefix__ is None:
            raise TypeError("describe() must be called on a subclass")
        return describe_instance(
            self.__bin_plan__,
            self,
            self.__bin_prefix__,
            prefix_enum,
            bool_as_int,
            enum_as_name,
        )

    @classmethod
    def try_unpack(
            cls,
            packed: str,
            expected: Optional[Union[Type[BinaryCallbackDataT], Type]] = None,
    ) -> Optional[BinaryCallbackDataT]:
        header = cls.get_header(packed)
        if header is None:
            return None
        resolved_cls = resolve(header.prefix, header.version)
        if resolved_cls is None:
            return None

        if expected is not None:
            allowed_classes = expand_expected_types(expected)
            for allowed in allowed_classes:
                if allowed is BinaryCallbackData or not issubclass(allowed, BinaryCallbackData):
                    raise ExpectedTypeError(
                        f"{allowed!r} is not a valid BinaryCallbackData subclass"
                    )
            if not issubclass(resolved_cls, allowed_classes):
                return None

        return cast(BinaryCallbackDataT, resolved_cls.unpack(packed))

    @classmethod
    def unpack(cls, packed: str) -> "BinaryCallbackData":
        try:
            raw = get_cipher().decrypt(get_wire_codec().decode(packed))
            prefix, version = decode_header(raw)
            if prefix != cls.__bin_prefix__:
                raise PrefixMismatchError(prefix, cls.__bin_prefix__)
            if version != cls.__bin_version__:
                raise VersionMismatchError(version, cls.__bin_version__)
            data, _ = decode_fields(cls.__bin_plan__, raw, HEADER_BITS)
            return cls(**data)
        except BinaryCallbackError:
            raise
        except Exception as error:
            raise DecodeError(str(error)) from error
