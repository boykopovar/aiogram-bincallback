# Enum-поля

```python
class Status(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"


status: Status = bfield(bits=4)
```

Поддерживается любой подкласс `Enum` (`Enum`, `IntEnum`, `str`-based `Enum`). Тип members не важен - на проводе передается позиционный индекс члена в `bin_order`, не само значение.

## bits

Обязателен, иначе `MissingBitsError`.

Минимум бит = `ceil(log2(len(bin_order)))`, не меньше 1 при количестве членов больше одного. Если `2 ** bits < len(bin_order)` - `InsufficientBitsError` с указанием требуемого числа бит.

Особый случай: enum с одним членом - допустим `bits=0`, поле не занимает бит на проводе. Отрицательный `bits` для одного члена все равно дает `InsufficientBitsError` (`2 ** bits < 1`).

## bin_order

Необязателен. Задает:

1. порядок кодирования членов в биты (индекс в кортеже = записанное число);
2. допустимое подмножество членов для этого поля.

Если не передан - `tuple(EnumCls)` (порядок объявления). Может быть строгим подмножеством всех членов - остальные требуют меньше бит и в кодировании не участвуют.

Дубликат члена в `bin_order` - `DuplicateBinOrderError`.

## signed, item_bits, max_len

Не применимы. Передача любого из них (в т.ч. `signed=False`) - `UnrecognizedBinFieldParamError`.

## Кодирование

Упаковка: `bin_order.index(value)`, записывается в `bits` бит как unsigned. Распаковка: индекс читается и превращается в `bin_order[index]`.

Значение вне `bin_order` во время `pack()` - `bin_order.index(value)` выбрасывает `ValueError` (не оборачивается в собственное исключение библиотеки).

Далее: [Списки enum](05-enum-lists.md).
