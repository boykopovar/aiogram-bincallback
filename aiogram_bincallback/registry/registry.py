from typing import Dict

from aiogram_bincallback.core import AIOGRAM_PREFIX_TEMPLATE
from aiogram_bincallback.core import PrefixCollisionError

_prefix_registry: Dict[int, type] = {}


def register(prefix: int, cls: type) -> None:
    existing_cls = _prefix_registry.get(prefix)
    if existing_cls is not None and existing_cls is not cls:
        raise PrefixCollisionError(prefix, existing_cls.__name__, cls.__name__)
    _prefix_registry[prefix] = cls


def make_aiogram_prefix(prefix: int) -> str:
    return AIOGRAM_PREFIX_TEMPLATE.format(prefix=prefix)
