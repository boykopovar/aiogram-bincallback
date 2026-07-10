from typing import TYPE_CHECKING
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type

from aiogram_bincallback.core import AIOGRAM_PREFIX_TEMPLATE
from aiogram_bincallback.core import PrefixCollisionError

if TYPE_CHECKING:
    from aiogram_bincallback.base import BinaryCallbackData

_prefix_registry: Dict[Tuple[int, int], Type["BinaryCallbackData"]] = {}


def register(prefix: int, version: int, cls: Type["BinaryCallbackData"]) -> None:
    key = (prefix, version)
    existing_cls = _prefix_registry.get(key)
    if existing_cls is not None and existing_cls is not cls:
        raise PrefixCollisionError(prefix, existing_cls.__name__, cls.__name__)
    _prefix_registry[key] = cls


def resolve(prefix: int, version: int) -> Optional[Type["BinaryCallbackData"]]:
    return _prefix_registry.get((prefix, version))


def make_aiogram_prefix(prefix: int) -> str:
    return AIOGRAM_PREFIX_TEMPLATE.format(prefix=prefix)
