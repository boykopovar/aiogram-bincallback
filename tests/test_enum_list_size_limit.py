from enum import Enum
from typing import List

import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import SizeLimitExceededError
from aiogram_bincallback import bfield
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS


class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


def test_enum_list_within_payload_budget_does_not_raise():
    class WithinBudgetCb(BinaryCallbackData, prefix=8201, version=1):
        path: List[Direction] = bfield(max_len=4)

    assert WithinBudgetCb.__bin_prefix__ == 8201


def test_enum_list_exceeding_payload_budget_raises_size_limit_exceeded_error():
    huge_max_len = MAX_PAYLOAD_BITS

    with pytest.raises(SizeLimitExceededError):
        class TooLargeCb(BinaryCallbackData, prefix=8202, version=1):
            path: List[Direction] = bfield(max_len=huge_max_len)


def test_enum_list_size_accounting_uses_worst_case_max_len_not_actual_length():
    from aiogram_bincallback.planning import build_codec_plan
    from aiogram_bincallback.planning import plan_total_bits
    from pydantic import BaseModel

    from tests.conftest import planning_bfield

    class Model(BaseModel):
        path: List[Direction] = planning_bfield(max_len=6)

    plan = build_codec_plan(Model)

    len_bits = 3
    item_bits = 2
    assert plan_total_bits(plan) == len_bits + 6 * item_bits
