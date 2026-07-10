from enum import Enum

from aiogram_bincallback import BinaryCallbackData, bfield


class Action(Enum):
    OPEN = 3

class OpenCb(BinaryCallbackData, prefix=3, version=1):
    x: int = bfield(bits=8, signed=False)

cb = OpenCb(x=5)
print(cb.describe(Action))
