from dataclasses import dataclass
from enum import Enum
from typing import Any
from typing import Generic
from typing import List
from typing import Optional
from typing import Sequence
from typing import Set
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import get_origin

from pydantic import BaseModel
from pydantic.fields import FieldInfo

from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_PLAN_ATTR
from aiogram_bincallback.core import BIN_SIGNED_KEY
from aiogram_bincallback.core import CircularNestingError
from aiogram_bincallback.core import DEFAULT_BOOL_BITS
from aiogram_bincallback.core import DEFAULT_INT_BITS
from aiogram_bincallback.core import DuplicateBinOrderError
from aiogram_bincallback.core import InsufficientBitsError
from aiogram_bincallback.core import MissingBitsError
from aiogram_bincallback.core import MissingSignedError
from aiogram_bincallback.core import NestedCallbackDataError
from aiogram_bincallback.core import SignedNotApplicableError
from aiogram_bincallback.core import UnsupportedFieldTypeError

_PATH_SEPARATOR = "."

EnumT = TypeVar("EnumT", bound=Enum)


@dataclass(frozen=True)
class BoolFieldCodec:
    name: str
    path: str
    optional: bool


@dataclass(frozen=True)
class IntFieldCodec:
    name: str
    path: str
    bits: int
    signed: bool
    optional: bool


@dataclass(frozen=True)
class EnumFieldCodec(Generic[EnumT]):
    name: str
    path: str
    bits: int
    bin_order: Tuple[EnumT, ...]
    enum_cls: Type[EnumT]
    optional: bool


@dataclass(frozen=True)
class NestedFieldCodec:
    name: str
    path: str
    model_cls: Type[BaseModel]
    plan: "CodecPlan"
    optional: bool


FieldCodec = Union[BoolFieldCodec, IntFieldCodec, EnumFieldCodec, NestedFieldCodec]
CodecPlan = List[FieldCodec]


def build_codec_plan(
    model_cls: Type[BaseModel],
    path: Optional[str] = None,
    visited: Optional[Sequence[type]] = None,
) -> CodecPlan:
    if visited is not None and model_cls in visited:
        raise CircularNestingError(path or model_cls.__name__, model_cls.__name__)
    current_visited = (*(visited or ()), model_cls)
    plan: CodecPlan = []
    for field_name, field_info in model_cls.model_fields.items():
        field_path = extend_path(path, field_name)
        plan.append(_build_field_codec(field_name, field_info, field_path, current_visited))
    return plan


def extend_path(path: Optional[str], field_name: str) -> str:
    if path is None:
        return field_name
    return f"{path}{_PATH_SEPARATOR}{field_name}"


def build_primitive_codec(
    field_name: str,
    field_info: FieldInfo,
    path: str,
) -> FieldCodec:
    annotation, optional = _unwrap_optional(field_info.annotation, path)
    return _build_primitive_codec(field_name, field_info, path, annotation, optional)


def plan_total_bits(plan: CodecPlan) -> int:
    return sum(_field_codec_bits(codec) for codec in plan)


def _build_field_codec(
    field_name: str,
    field_info: FieldInfo,
    path: str,
    visited: Sequence[type],
) -> FieldCodec:
    annotation, optional = _unwrap_optional(field_info.annotation, path)
    if hasattr(annotation, BIN_PLAN_ATTR):
        raise NestedCallbackDataError(path)
    if _is_nested_model(annotation):
        nested_plan = build_codec_plan(annotation, path, visited)
        return NestedFieldCodec(
            name=field_name,
            path=path,
            model_cls=annotation,
            plan=nested_plan,
            optional=optional,
        )
    return _build_primitive_codec(field_name, field_info, path, annotation, optional)


def _unwrap_optional(annotation: Any, path: str) -> Tuple[Any, bool]:
    if get_origin(annotation) is not Union:
        return annotation, False
    args = get_args(annotation)
    non_none_args = tuple(arg for arg in args if arg is not type(None))
    if len(non_none_args) != 1 or len(non_none_args) == len(args):
        raise UnsupportedFieldTypeError(path, annotation)
    return non_none_args[0], True


def _is_nested_model(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, BaseModel)


def _is_enum_type(annotation: Any) -> bool:
    return isinstance(annotation, type) and issubclass(annotation, Enum)


def _build_primitive_codec(
    field_name: str,
    field_info: FieldInfo,
    path: str,
    annotation: Any,
    optional: bool,
) -> FieldCodec:
    extra = field_info.json_schema_extra or {}
    bits = extra.get(BIN_BITS_KEY)
    signed = extra.get(BIN_SIGNED_KEY)
    bin_order = extra.get(BIN_ORDER_KEY)
    if annotation is bool:
        return _build_bool_codec(field_name, path, signed, optional)
    if annotation is int:
        return _build_int_codec(field_name, path, bits, signed, optional)
    if _is_enum_type(annotation):
        return _build_enum_codec(field_name, path, bits, bin_order, annotation, optional)
    raise UnsupportedFieldTypeError(path, annotation)


def _build_bool_codec(
    field_name: str,
    path: str,
    signed: Optional[bool],
    optional: bool,
) -> BoolFieldCodec:
    if signed is not None:
        raise SignedNotApplicableError(path, bool)
    return BoolFieldCodec(name=field_name, path=path, optional=optional)


def _build_int_codec(
    field_name: str,
    path: str,
    bits: Optional[int],
    signed: Optional[bool],
    optional: bool,
) -> IntFieldCodec:
    if signed is None:
        raise MissingSignedError(path)
    resolved_bits = bits if bits is not None else DEFAULT_INT_BITS
    return IntFieldCodec(
        name=field_name,
        path=path,
        bits=resolved_bits,
        signed=signed,
        optional=optional,
    )


def _build_enum_codec(
    field_name: str,
    path: str,
    bits: Optional[int],
    bin_order: Optional[Sequence[EnumT]],
    enum_cls: Type[EnumT],
    optional: bool,
) -> EnumFieldCodec:
    if bits is None:
        raise MissingBitsError(path)
    resolved_bin_order = _resolve_bin_order(path, bin_order, enum_cls)
    required_bits = _minimum_bits_for_count(len(resolved_bin_order))
    if 2 ** bits < len(resolved_bin_order):
        raise InsufficientBitsError(path, bits, required_bits)
    return EnumFieldCodec(
        name=field_name,
        path=path,
        bits=bits,
        bin_order=resolved_bin_order,
        enum_cls=enum_cls,
        optional=optional,
    )


def _resolve_bin_order(
    path: str,
    bin_order: Optional[Sequence[EnumT]],
    enum_cls: Type[EnumT],
) -> Tuple[EnumT, ...]:
    members = tuple(enum_cls) if bin_order is None else tuple(bin_order)
    _check_no_duplicate_members(path, members)
    return members


def _check_no_duplicate_members(path: str, members: Sequence[Enum]) -> None:
    seen_names: Set[str] = set()
    for member in members:
        if member.name in seen_names:
            raise DuplicateBinOrderError(path, member.name)
        seen_names.add(member.name)


def _minimum_bits_for_count(count: int) -> int:
    if count <= 1:
        return 1
    bits = 0
    while (1 << bits) < count:
        bits += 1
    return bits


def _field_codec_bits(codec: FieldCodec) -> int:
    presence_bit = 1 if codec.optional else 0
    return presence_bit + _inner_field_bits(codec)


def _inner_field_bits(codec: FieldCodec) -> int:
    if isinstance(codec, BoolFieldCodec):
        return DEFAULT_BOOL_BITS
    if isinstance(codec, IntFieldCodec):
        return codec.bits
    if isinstance(codec, EnumFieldCodec):
        return codec.bits
    return plan_total_bits(codec.plan)
