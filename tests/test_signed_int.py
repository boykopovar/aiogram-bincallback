import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import DEFAULT_INT_BITS
from aiogram_bincallback.core import MissingSignedError
from aiogram_bincallback.planning import IntFieldCodec
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


def test_signed_int_field_produces_int_codec_with_signed_true():
    class Model(BaseModel):
        value: int = planning_bfield(bits=16, signed=True)

    plan = build_codec_plan(Model)

    assert plan == [IntFieldCodec(name="value", path="value", bits=16, signed=True, optional=False)]


def test_unsigned_int_field_produces_int_codec_with_signed_false():
    class Model(BaseModel):
        value: int = planning_bfield(bits=16, signed=False)

    plan = build_codec_plan(Model)

    assert plan == [IntFieldCodec(name="value", path="value", bits=16, signed=False, optional=False)]


def test_int_field_without_bits_falls_back_to_default_int_bits():
    class Model(BaseModel):
        value: int = planning_bfield(signed=False)

    plan = build_codec_plan(Model)

    assert plan[0].bits == DEFAULT_INT_BITS


def test_int_field_without_signed_raises_missing_signed_error():
    class Model(BaseModel):
        value: int = planning_bfield(bits=8)

    with pytest.raises(MissingSignedError) as excinfo:
        build_codec_plan(Model)

    assert "value" in str(excinfo.value)
