from typing import Tuple

from aiogram_bincallback.bitstream import BitReader
from aiogram_bincallback.bitstream import BitWriter
from aiogram_bincallback.core import PREFIX_BITS
from aiogram_bincallback.core import SizeLimitExceededError
from aiogram_bincallback.core import VERSION_BITS
from aiogram_bincallback.planning import CodecPlan
from aiogram_bincallback.planning import plan_total_bits


def encode_header(prefix: int, version: int) -> bytes:
    writer = BitWriter()
    writer.write_uint(prefix, PREFIX_BITS)
    writer.write_uint(version, VERSION_BITS)
    return writer.to_bytes()


def decode_header(data: bytes) -> Tuple[int, int]:
    reader = BitReader(data)
    prefix = reader.read_uint(PREFIX_BITS)
    version = reader.read_uint(VERSION_BITS)
    return prefix, version


def check_size_limit(plan: CodecPlan, max_payload_bits: int) -> None:
    total_bits = plan_total_bits(plan)
    if total_bits > max_payload_bits:
        raise SizeLimitExceededError(total_bits, max_payload_bits)
