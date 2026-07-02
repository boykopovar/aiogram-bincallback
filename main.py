from enum import Enum, IntEnum

from aiogram_bincallback import BinaryCallbackData, bfield


class CbPrefix(IntEnum):
    ORDER = 1
    HOME = 2


class Status(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"


class OrderCb(BinaryCallbackData, prefix=CbPrefix.ORDER.value, version=1):
    order_id: int = bfield(bits=16, signed=False)
    status: Status = bfield(bits=4)
