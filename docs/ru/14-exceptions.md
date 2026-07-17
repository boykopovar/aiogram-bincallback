# Исключения

Корень иерархии - `BinaryCallbackError(ValueError)`. Все исключения библиотеки - его подклассы, кроме `PrefixEnumMismatchError`, который наследуется от `BinaryCallbackError` напрямую вне ветвей ниже.

## Иерархия

```
BinaryCallbackError
├── DefinitionError
│   ├── UnsupportedFieldTypeError
│   ├── MissingBitsError
│   ├── InsufficientBitsError
│   ├── DuplicateBinOrderError
│   ├── MissingMaxLenError
│   ├── BitsNotApplicableToListError
│   ├── SignedNotApplicableError
│   ├── MissingSignedError
│   ├── NestedCallbackDataError
│   ├── CircularNestingError
│   ├── SizeLimitExceededError
│   ├── PrefixCollisionError
│   └── ExpectedTypeError
├── EncodeError
│   ├── ValueOverflowError
│   └── ListLengthOverflowError
├── DecodeError
│   ├── PrefixMismatchError
│   ├── VersionMismatchError
│   ├── PayloadCorruptError
│   └── DecryptionError
├── PrefixEnumMismatchError
└── CipherReconfiguredAfterUseError
```

## DefinitionError - ошибки при определении класса

| Класс                          | Когда возникает                                                                 |
|--------------------------------|-----------------------------------------------------------------------------------|
| `UnsupportedFieldTypeError`    | аннотация поля не входит в поддерживаемый набор типов (раздел 3)                  |
| `MissingBitsError`             | `int`-поле без обязательного `bits`                                              |
| `InsufficientBitsError`        | `bits`/`item_bits` enum-поля меньше минимума для `len(bin_order)` значений         |
| `DuplicateBinOrderError`       | повтор одного члена enum в `bin_order`                                            |
| `MissingMaxLenError`           | `List[Enum]`-поле без обязательного `max_len`                                     |
| `BitsNotApplicableToListError` | `bits` передан для `List[Enum]`-поля                                              |
| `SignedNotApplicableError`     | `signed` передан для типа, где он не применим (`bool`, `Enum`, `List[Enum]`, вложенная модель) |
| `MissingSignedError`           | `int`-поле без обязательного `signed`                                             |
| `NestedCallbackDataError`      | поле ссылается на подкласс `BinaryCallbackData` вместо обычного `BaseModel`        |
| `CircularNestingError`         | вложенная модель прямо или через несколько уровней ссылается сама на себя         |
| `SizeLimitExceededError`       | суммарный бюджет бит класса превышает `MAX_PAYLOAD_BITS`                          |
| `PrefixCollisionError`         | пара `(prefix, version)` уже занята другим классом в реестре                      |
| `ExpectedTypeError`            | элемент `expected` в `try_unpack` - не подкласс `BinaryCallbackData` либо сам `BinaryCallbackData` |

Все `DefinitionError` проявляются при импорте модуля с определением класса (`__pydantic_init_subclass__`), кроме `ExpectedTypeError`, который возникает при вызове `try_unpack`.

## EncodeError - ошибки при упаковке

| Класс                     | Когда возникает                                                  |
|---------------------------|----------------------------------------------------------------------|
| `ValueOverflowError`      | значение `int`-поля выходит за границы, заданные `bits` и `signed`   |
| `ListLengthOverflowError` | фактическая длина `List[Enum]`-поля больше `max_len`                 |

Обе проверяются только на `pack()` / `encode_fields`, не при создании pydantic-модели.

## DecodeError - ошибки при распаковке

| Класс                  | Когда возникает                                                        |
|-------------------------|----------------------------------------------------------------------------|
| `PrefixMismatchError`  | декодированный `prefix` не совпадает с `prefix` класса, на котором вызван `unpack` |
| `VersionMismatchError` | декодированная `version` не совпадает с `version` класса                    |
| `PayloadCorruptError`  | символ вне base128-алфавита, отсутствующий или испорченный бит-маркер длины  |
| `DecryptionError`      | ошибка на стороне пользовательской реализации `ICipher.decrypt`             |

Любая иная ошибка внутри `unpack`, не являющаяся `BinaryCallbackError`, оборачивается в `DecodeError` с текстом исходного исключения.

## Прочие

| Класс                          | Когда возникает                                                                |
|--------------------------------|------------------------------------------------------------------------------------|
| `PrefixEnumMismatchError`      | в `describe(prefix_enum=...)` нет члена с `value == prefix`                        |
| `CipherReconfiguredAfterUseError` | повторный `configure(cipher=...)` с другим объектом шифра после того, как прежний уже использовался в `pack`/`unpack`/`get_header` |

## try_unpack и is_valid не выбрасывают исключения

`try_unpack` возвращает `None` вместо исключения при нечитаемом заголовке, незарегистрированной паре `(prefix, version)` или несовпадении с `expected` - кроме случая некорректного самого `expected`, тогда `ExpectedTypeError` выбрасывается. `is_valid` и `get_header` возвращают `False`/`None` на любой ошибке декодирования, ничего не пробрасывают.
