from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar

from pydantic import BaseModel

from aiogram_bincallback.bitstream.bitstream import BitReader
from aiogram_bincallback.bitstream.bitstream import BitWriter
from aiogram_bincallback.core.constants import DEFAULT_BOOL_BITS
from aiogram_bincallback.core.constants import DESCRIBE_FIELD_SEPARATOR
from aiogram_bincallback.core.exceptions import PrefixEnumMismatchError
from aiogram_bincallback.core.exceptions import ValueOverflowError
from aiogram_bincallback.planning.planning import BoolFieldCodec
from aiogram_bincallback.planning.planning import CodecPlan
from aiogram_bincallback.planning.planning import EnumFieldCodec
from aiogram_bincallback.planning.planning import FieldCodec
from aiogram_bincallback.planning.planning import IntFieldCodec
from aiogram_bincallback.planning.planning import NestedFieldCodec

PrefixEnumT = TypeVar("PrefixEnumT", bound=Enum)


def encode_fields(plan: CodecPlan, instance: BaseModel) -> bytes:
    writer = BitWriter()
    _encode_fields_into(plan, instance, writer)
    return writer.to_bytes()


def decode_fields(plan: CodecPlan, data: bytes, start_bit: int) -> Tuple[Dict[str, Any], int]:
    reader = BitReader(data, start_bit)
    values = _decode_fields_from(plan, reader)
    return values, reader.position_bits


def describe_fields(plan: CodecPlan, instance: BaseModel) -> List[str]:
    tokens: List[str] = []
    for codec in plan:
        value = getattr(instance, codec.name)
        tokens.append(_describe_field(codec, value))
    return tokens


def describe_instance(
    plan: CodecPlan,
    instance: BaseModel,
    prefix: int,
    prefix_enum: Optional[Type[PrefixEnumT]],
) -> str:
    tokens = [_resolve_prefix_token(prefix, prefix_enum), *describe_fields(plan, instance)]
    return DESCRIBE_FIELD_SEPARATOR.join(tokens)


def _describe_field(codec: FieldCodec, value: Any) -> str:
    if value is None:
        return str(value)
    if isinstance(codec, NestedFieldCodec):
        return DESCRIBE_FIELD_SEPARATOR.join(describe_fields(codec.plan, value))
    if isinstance(codec, EnumFieldCodec):
        return value.name
    return str(value)


def _resolve_prefix_token(prefix: int, prefix_enum: Optional[Type[PrefixEnumT]]) -> str:
    if prefix_enum is None:
        return str(prefix)
    for member in prefix_enum:
        if member.value == prefix:
            return member.name
    raise PrefixEnumMismatchError(prefix, prefix_enum)


def _encode_fields_into(plan: CodecPlan, instance: BaseModel, writer: BitWriter) -> None:
    for codec in plan:
        value = getattr(instance, codec.name)
        if codec.optional:
            writer.write_uint(int(value is not None), DEFAULT_BOOL_BITS)
            if value is None:
                continue
        _write_field(writer, codec, value)


def _decode_fields_from(plan: CodecPlan, reader: BitReader) -> Dict[str, Any]:
    values: Dict[str, Any] = {}
    for codec in plan:
        if codec.optional and not reader.read_uint(DEFAULT_BOOL_BITS):
            values[codec.name] = None
            continue
        values[codec.name] = _read_field(reader, codec)
    return values


def _write_field(writer: BitWriter, codec: FieldCodec, value: Any) -> None:
    if isinstance(codec, BoolFieldCodec):
        writer.write_uint(int(value), DEFAULT_BOOL_BITS)
        return
    if isinstance(codec, IntFieldCodec):
        _check_int_overflow(codec, value)
        if codec.signed:
            writer.write_int(value, codec.bits)
        else:
            writer.write_uint(value, codec.bits)
        return
    if isinstance(codec, EnumFieldCodec):
        writer.write_uint(codec.bin_order.index(value), codec.bits)
        return
    _encode_fields_into(codec.plan, value, writer)


def _read_field(reader: BitReader, codec: FieldCodec) -> Any:
    if isinstance(codec, BoolFieldCodec):
        return bool(reader.read_uint(DEFAULT_BOOL_BITS))
    if isinstance(codec, IntFieldCodec):
        return reader.read_int(codec.bits) if codec.signed else reader.read_uint(codec.bits)
    if isinstance(codec, EnumFieldCodec):
        return codec.bin_order[reader.read_uint(codec.bits)]
    return _decode_fields_from(codec.plan, reader)


def _check_int_overflow(codec: IntFieldCodec, value: int) -> None:
    lower_bound, upper_bound = _int_bounds(codec.bits, codec.signed)
    if value < lower_bound or value > upper_bound:
        raise ValueOverflowError(codec.path, value, codec.bits, codec.signed)


def _int_bounds(bits: int, signed: bool) -> Tuple[int, int]:
    if signed:
        return -(1 << (bits - 1)), (1 << (bits - 1)) - 1
    return 0, (1 << bits) - 1
