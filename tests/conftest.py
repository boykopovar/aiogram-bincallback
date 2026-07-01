from enum import Enum
from typing import Optional
from typing import Sequence

from pydantic import Field
from pydantic.fields import FieldInfo

from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_SIGNED_KEY


def planning_bfield(
    *,
    bits: Optional[int] = None,
    bin_order: Optional[Sequence[Enum]] = None,
    signed: Optional[bool] = None,
) -> FieldInfo:
    return Field(
        json_schema_extra={
            BIN_BITS_KEY: bits,
            BIN_ORDER_KEY: bin_order,
            BIN_SIGNED_KEY: signed,
        }
    )
