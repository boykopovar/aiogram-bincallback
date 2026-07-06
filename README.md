# aiogram-bincallback

Библиотека для aiogram 3.x, сериализующая CallbackData в бинарном виде вместо текстового формата key:value. Каждое поле упаковывается в заданное число бит, что позволяет уместить больше данных в лимит Telegram на callback_data в 64 байта и явно контролировать структуру данных.

## Установка

```
pip install -U git+ssh://git@github.com/boykopovar/aiogram-bincallback.git
```

## Использование

```python
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
```

Поддерживаемые типы полей, правила вложенности и обработка ошибок описаны в тестах в директории `tests/`.
