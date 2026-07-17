from enum import Enum
from typing import List
from typing import Optional

import pytest
from pydantic import BaseModel

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import ListLengthOverflowError
from aiogram_bincallback import bfield
from aiogram_bincallback.codec import decode_fields
from aiogram_bincallback.codec import describe_fields
from aiogram_bincallback.codec import encode_fields
from aiogram_bincallback.codec import EnumListDescribeOptions
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


def test_enum_list_roundtrips_through_encode_and_decode():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.LEFT, Direction.LEFT])

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": [Direction.UP, Direction.LEFT, Direction.LEFT]}


def test_enum_list_roundtrips_empty_list():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[])

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": []}


def test_enum_list_roundtrips_at_exact_max_len():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=3)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN, Direction.LEFT])

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": [Direction.UP, Direction.DOWN, Direction.LEFT]}


def test_enum_list_roundtrips_with_duplicate_values():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.UP, Direction.UP])

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": [Direction.UP, Direction.UP, Direction.UP]}


def test_enum_list_exceeding_max_len_raises_list_length_overflow_error():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=2)

    plan = build_codec_plan(Model)
    instance = Model.model_construct(path=[Direction.UP, Direction.DOWN, Direction.LEFT])

    with pytest.raises(ListLengthOverflowError) as excinfo:
        encode_fields(plan, instance)

    assert "path" in str(excinfo.value)


def test_optional_enum_list_roundtrips_none():
    class Model(BaseModel):
        path: Optional[List[Direction]] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=None)

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": None}


def test_optional_enum_list_roundtrips_present_value():
    class Model(BaseModel):
        path: Optional[List[Direction]] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.RIGHT])

    data = encode_fields(plan, instance)
    decoded, _ = decode_fields(plan, data, 0)

    assert decoded == {"path": [Direction.RIGHT]}


def test_enum_list_describe_joins_member_names_with_list_separator():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True)

    assert tokens == ["[UP,DOWN]"]


def test_enum_list_describe_ignores_enum_as_name_flag():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=False)

    assert tokens == ["[UP,DOWN]"]


def test_enum_list_describe_joins_member_values_when_enum_list_as_name_false():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    options = EnumListDescribeOptions(as_name=False)
    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True, enum_list_options=options)

    assert tokens == ["[up,down]"]


def test_enum_list_describe_uses_custom_separator():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    options = EnumListDescribeOptions(separator="|")
    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True, enum_list_options=options)

    assert tokens == ["[UP|DOWN]"]


def test_enum_list_describe_without_brackets():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    options = EnumListDescribeOptions(brackets=False)
    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True, enum_list_options=options)

    assert tokens == ["UP,DOWN"]


def test_enum_list_describe_empty_separator_and_no_brackets():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[Direction.UP, Direction.DOWN])

    options = EnumListDescribeOptions(as_name=False, separator="", brackets=False)
    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True, enum_list_options=options)

    assert tokens == ["updown"]


def test_enum_list_describe_empty_list_is_empty_token():
    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=[])

    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True)

    assert tokens == ["[]"]


def test_optional_enum_list_describe_none_as_none_token():
    class Model(BaseModel):
        path: Optional[List[Direction]] = planning_bfield(max_len=5)

    plan = build_codec_plan(Model)
    instance = Model(path=None)

    tokens = describe_fields(plan, instance, bool_as_int=True, enum_as_name=True)

    assert tokens == ["None"]


class RouteCb(BinaryCallbackData, prefix=8101, version=1):
    path: List[Direction] = bfield(max_len=4)


def test_binary_callback_data_packs_and_unpacks_enum_list_field():
    instance = RouteCb(path=[Direction.UP, Direction.RIGHT, Direction.RIGHT])

    packed = instance.pack()
    unpacked = RouteCb.unpack(packed)

    assert unpacked.path == [Direction.UP, Direction.RIGHT, Direction.RIGHT]


def test_binary_callback_data_packs_and_unpacks_empty_enum_list_field():
    instance = RouteCb(path=[])

    packed = instance.pack()
    unpacked = RouteCb.unpack(packed)

    assert unpacked.path == []


def test_binary_callback_data_describe_includes_enum_list_as_joined_names():
    instance = RouteCb(path=[Direction.UP, Direction.DOWN])

    assert instance.describe() == "8101:[UP,DOWN]"
