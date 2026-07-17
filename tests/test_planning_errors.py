from enum import Enum
from typing import List

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import UnrecognizedBinFieldParamError
from aiogram_bincallback.core import UnsupportedFieldTypeError
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


def test_unsupported_field_type_raises_with_field_path():
    class Model(BaseModel):
        tags: List[str] = planning_bfield()

    with pytest.raises(UnsupportedFieldTypeError) as excinfo:
        build_codec_plan(Model)

    assert "tags" in str(excinfo.value)


def test_unsupported_field_type_reports_dotted_path_when_nested():
    class Inner(BaseModel):
        tags: List[str] = planning_bfield()

    class Outer(BaseModel):
        inner: Inner

    with pytest.raises(UnsupportedFieldTypeError) as excinfo:
        build_codec_plan(Outer)

    assert "inner.tags" in str(excinfo.value)


def test_signed_passed_for_bool_field_raises_unrecognized_bin_field_param_error():
    class Model(BaseModel):
        flag: bool = planning_bfield(signed=False)

    with pytest.raises(UnrecognizedBinFieldParamError) as excinfo:
        build_codec_plan(Model)

    assert "flag" in str(excinfo.value)


def test_signed_passed_for_enum_field_raises_unrecognized_bin_field_param_error():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4, signed=False)

    with pytest.raises(UnrecognizedBinFieldParamError) as excinfo:
        build_codec_plan(Model)

    assert "status" in str(excinfo.value)


def test_signed_passed_for_nested_basemodel_raises_unrecognized_bin_field_param_error():
    class Inner(BaseModel):
        value: int = planning_bfield(bits=4, signed=False)

    class Outer(BaseModel):
        inner: Inner = planning_bfield(signed=False)

    with pytest.raises(UnrecognizedBinFieldParamError) as excinfo:
        build_codec_plan(Outer)

    assert "inner" in str(excinfo.value)


def test_signed_passed_for_enum_field_raises_unrecognized_bin_field_param_error_through_binary_callback_data():
    from aiogram_bincallback import BinaryCallbackData
    from aiogram_bincallback import bfield

    with pytest.raises(UnrecognizedBinFieldParamError):
        class EnumSignedCb(BinaryCallbackData, prefix=9501, version=1):
            status: Status = bfield(bits=4, signed=False, bin_order=(Status.ACTIVE, Status.DONE))


def test_signed_passed_for_nested_basemodel_raises_unrecognized_bin_field_param_error_through_binary_callback_data():
    from aiogram_bincallback import BinaryCallbackData
    from aiogram_bincallback import bfield

    class InnerModel(BaseModel):
        value: int = bfield(bits=4, signed=False)

    with pytest.raises(UnrecognizedBinFieldParamError):
        class NestedSignedCb(BinaryCallbackData, prefix=9502, version=1):
            inner: InnerModel = bfield(signed=False)
