from enum import Enum

import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import MissingBinOrderError
from aiogram_bincallback.planning import build_codec_plan

from tests.conftest import planning_bfield


class Status(str, Enum):
    ACTIVE = "active"
    DONE = "done"


def test_enum_field_without_bin_order_raises_missing_bin_order_error():
    class Model(BaseModel):
        status: Status = planning_bfield(bits=4)

    with pytest.raises(MissingBinOrderError) as excinfo:
        build_codec_plan(Model)

    assert "status" in str(excinfo.value)
