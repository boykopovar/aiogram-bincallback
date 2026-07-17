# aiogram-bincallback

Побитовая сериализация CallbackData для aiogram 3.x вместо текстового формата `prefix:field1:field2`. Каждое поле занимает фиксированное число бит - в лимит Telegram (64 байта) помещается больше данных, размер payload известен на этапе определения класса.

## Установка

```
pip install aiogram-bincallback
```

Зависимости: `aiogram>=3.0,<4.0`, `pydantic>=2.0,<3.0`, Python 3.8+.


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

`prefix` и `version` - аргументы наследования класса, не поля модели. Оба обязательны.

```python
cb = OrderCb(order_id=42, status=Status.PENDING)
packed = cb.pack()
restored = OrderCb.unpack(packed)
```

`OrderCb` - одновременно `pydantic.BaseModel` и `aiogram.CallbackData`, используется в фильтрах как обычный `CallbackData`:

```python
from aiogram import Router

router = Router()


@router.callback_query(OrderCb.filter())
async def handle_order(callback, callback_data: OrderCb):
    ...
```

[Документация](https://github.com/boykopovar/aiogram-bincallback/blob/main/docs/ru/00-table-of-contents.md)
