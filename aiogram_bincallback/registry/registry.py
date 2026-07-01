from typing import Dict
from typing import Type


_prefix_registry: Dict[int, type] = {}


def register(prefix: int, cls: type) -> None:
    ...


def make_aiogram_prefix(prefix: int) -> str:
    ...
