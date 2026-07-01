import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import HEADER_BITS
from aiogram_bincallback.core import PREFIX_BITS
from aiogram_bincallback.core import SizeLimitExceededError
from aiogram_bincallback.core import VERSION_BITS
from aiogram_bincallback.header import check_size_limit
from aiogram_bincallback.header import decode_header
from aiogram_bincallback.header import encode_header
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


def test_encode_header_produces_exactly_header_bits_worth_of_bytes():
    packed = encode_header(prefix=1, version=1)

    assert len(packed) == HEADER_BITS // 8


def test_decode_header_reverses_encode_header():
    packed = encode_header(prefix=1234, version=7)

    prefix, version = decode_header(packed)

    assert (prefix, version) == (1234, 7)


def test_decode_header_reads_prefix_and_version_independently():
    packed = encode_header(prefix=0, version=0)

    assert decode_header(packed) == (0, 0)


def test_encode_header_respects_max_prefix_bits():
    max_prefix = (1 << PREFIX_BITS) - 1
    max_version = (1 << VERSION_BITS) - 1

    packed = encode_header(prefix=max_prefix, version=max_version)

    assert decode_header(packed) == (max_prefix, max_version)


def test_check_size_limit_passes_when_plan_fits_budget():
    class Model(BaseModel):
        flag: bool = planning_bfield(signed=None)

    plan = build_codec_plan(Model)

    check_size_limit(plan, max_payload_bits=1)


def test_check_size_limit_raises_when_plan_exceeds_budget():
    class Model(BaseModel):
        value: int = planning_bfield(bits=32, signed=False)

    plan = build_codec_plan(Model)

    with pytest.raises(SizeLimitExceededError) as excinfo:
        check_size_limit(plan, max_payload_bits=16)

    assert "32" in str(excinfo.value)
    assert "16" in str(excinfo.value)


def test_check_size_limit_allows_plan_exactly_at_budget():
    class Model(BaseModel):
        value: int = planning_bfield(bits=8, signed=False)

    plan = build_codec_plan(Model)

    check_size_limit(plan, max_payload_bits=8)
