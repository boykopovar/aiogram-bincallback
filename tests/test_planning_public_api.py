from enum import Enum
from typing import Optional
from typing import Union

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import UnsupportedFieldTypeError
from aiogram_bincallback.planning import BoolFieldCodec
from aiogram_bincallback.planning import EnumFieldCodec
from aiogram_bincallback.planning import IntFieldCodec
from aiogram_bincallback.planning import build_codec_plan
from aiogram_bincallback.planning import build_primitive_codec

from tests.conftest import planning_bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


def test_build_primitive_codec_builds_bool_codec_directly():
    class Model(BaseModel):
        flag: bool = planning_bfield()

    codec = build_primitive_codec("flag", Model.model_fields["flag"], "flag")

    assert codec == BoolFieldCodec(name="flag", path="flag", optional=False)


def test_build_primitive_codec_builds_int_codec_directly():
    class Model(BaseModel):
        value: int = planning_bfield(bits=8, signed=False)

    codec = build_primitive_codec("value", Model.model_fields["value"], "value")

    assert codec == IntFieldCodec(name="value", path="value", bits=8, signed=False, optional=False)


def test_build_primitive_codec_builds_enum_codec_directly():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=1, bin_order=(Status.ACTIVE, Status.DONE))

    codec = build_primitive_codec("status", Model.model_fields["status"], "status")

    assert codec == EnumFieldCodec(
        name="status",
        path="status",
        bits=1,
        bin_order=(Status.ACTIVE, Status.DONE),
        enum_cls=Status,
        optional=False,
    )


def test_build_primitive_codec_unwraps_optional_before_dispatching():
    class Model(BaseModel):
        value: Optional[int] = planning_bfield(bits=8, signed=False)

    codec = build_primitive_codec("value", Model.model_fields["value"], "value")

    assert codec == IntFieldCodec(name="value", path="value", bits=8, signed=False, optional=True)


def test_build_primitive_codec_raises_unsupported_field_type_for_unresolvable_union():
    class Model(BaseModel):
        value: Union[int, str] = planning_bfield(bits=8, signed=False)

    with pytest.raises(UnsupportedFieldTypeError):
        build_primitive_codec("value", Model.model_fields["value"], "value")


def test_multi_type_union_raises_unsupported_field_type_error_through_build_codec_plan():
    class Model(BaseModel):
        value: Union[int, str] = planning_bfield(bits=8, signed=False)

    with pytest.raises(UnsupportedFieldTypeError) as excinfo:
        build_codec_plan(Model)

    assert "value" in str(excinfo.value)


def test_optional_multi_type_union_raises_unsupported_field_type_error():
    class Model(BaseModel):
        value: Optional[Union[int, str]] = planning_bfield(bits=8, signed=False)

    with pytest.raises(UnsupportedFieldTypeError) as excinfo:
        build_codec_plan(Model)

    assert "value" in str(excinfo.value)
