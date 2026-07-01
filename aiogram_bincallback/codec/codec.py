from typing import Any
from typing import Dict
from typing import Tuple

from pydantic import BaseModel

from aiogram_bincallback.bitstream.bitstream import BitReader
from aiogram_bincallback.bitstream.bitstream import BitWriter
from aiogram_bincallback.planning import CodecPlan


def encode_fields(plan: CodecPlan, instance: BaseModel) -> bytes:
    ...


def decode_fields(plan: CodecPlan, data: bytes, start_bit: int) -> Tuple[Dict[str, Any], int]:
    ...


def _write_field(writer: BitWriter, codec: object, value: Any) -> None:
    ...


def _read_field(reader: BitReader, codec: object) -> Any:
    ...
