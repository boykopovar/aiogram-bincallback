from enum import Enum
from typing import Optional
from typing import Sequence

from pydantic import Field
from pydantic.fields import FieldInfo

import aiogram_bincallback.config.config as config_module
from aiogram_bincallback.core import BIN_BITS_KEY
from aiogram_bincallback.core import BIN_MAX_LEN_KEY
from aiogram_bincallback.core import BIN_ORDER_KEY
from aiogram_bincallback.core import BIN_SIGNED_KEY
from aiogram_bincallback.wire import Base128WireCodec
from aiogram_bincallback.wire import NullCipher


def planning_bfield(
    *,
    bits: Optional[int] = None,
    bin_order: Optional[Sequence[Enum]] = None,
    signed: Optional[bool] = None,
    max_len: Optional[int] = None,
) -> FieldInfo:
    return Field(
        json_schema_extra={
            BIN_BITS_KEY: bits,
            BIN_ORDER_KEY: bin_order,
            BIN_SIGNED_KEY: signed,
            BIN_MAX_LEN_KEY: max_len,
        }
    )


def reset_configuration() -> None:
    config_module._wire_codec = Base128WireCodec()
    config_module._cipher = NullCipher()
    config_module._cipher_used = False
