from dataclasses import dataclass
from dataclasses import field
from typing import List
from typing import Optional
from typing import Sequence
from typing import Tuple
from typing import Type
from typing import Union

from pydantic import BaseModel
from pydantic.fields import FieldInfo


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
class EnumFieldCodec:
    name: str
    path: str
    bits: int
    bin_order: Tuple[str, ...]
    enum_cls: type
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
    ...


def extend_path(path: Optional[str], field_name: str) -> str:
    ...


def build_primitive_codec(
    field_name: str,
    field_info: FieldInfo,
    path: str,
) -> FieldCodec:
    ...


def plan_total_bits(plan: CodecPlan) -> int:
    ...
