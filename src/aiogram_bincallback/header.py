from typing import Tuple
from typing import Type

from aiogram_bincallback.planning import CodecPlan


def encode_header(prefix: int, version: int) -> bytes:
    ...


def decode_header(data: bytes) -> Tuple[int, int]:
    ...


def check_size_limit(plan: CodecPlan) -> None:
    ...
