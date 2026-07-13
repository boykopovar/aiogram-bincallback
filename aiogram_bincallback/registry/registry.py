from typing import TYPE_CHECKING
from typing import Dict
from typing import Optional
from typing import Tuple
from typing import Type
from typing import Union
from typing import get_args
from typing import get_origin

from aiogram_bincallback.core import AIOGRAM_PREFIX_TEMPLATE
from aiogram_bincallback.core import ExpectedTypeError
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


def expand_expected_types(
    expected: object,
) -> Tuple[Type["BinaryCallbackData"], ...]:
    from aiogram_bincallback.base import BinaryCallbackData

    candidates: Tuple[object, ...]
    if get_origin(expected) is Union:
        candidates = get_args(expected)
    else:
        candidates = (expected,)

    result = []
    for candidate in candidates:
        if (
            not isinstance(candidate, type)
            or not issubclass(candidate, BinaryCallbackData)
            or candidate is BinaryCallbackData
        ):
            raise ExpectedTypeError(candidate)
        result.append(candidate)
    return tuple(result)
