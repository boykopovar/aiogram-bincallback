# Типы полей

Поддерживаемые аннотации: `bool`, `int`, подклассы `Enum`, `List[EnumT]`, вложенные `BaseModel`, любой из них обернутый в `Optional[...]`.

Любая другая аннотация (`str`, `float`, `List[int]`, `List[Optional[Enum]]`, `Union[int, str]`) - `UnsupportedFieldTypeError` при построении плана кодека.

## bool

```python
flag: bool = bfield()
```

- ровно 1 бит (`DEFAULT_BOOL_BITS`);
- `bits` не применим, `signed` запрещен;
- кодируется как `int(value)`, декодируется через `bool(...)`.

## int

```python
value: int = bfield(bits=16, signed=False)
```

| Параметр | Обязателен | По умолчанию |
|----------|------------|--------------|
| `signed` | да         | -            |
| `bits`   | нет        | 32           |

Границы: `signed=True` -> `-(2**(bits-1))` .. `2**(bits-1)-1`. `signed=False` -> `0` .. `2**bits-1`.

Выход за границы не обнаруживается при определении класса и не при создании pydantic-модели - только при `pack()` / `encode_fields`, результат - `ValueOverflowError`. Граничные значения проходят без ошибки.

## Enum

См. [раздел 4](04-enum-fields.md).

## List[Enum]

См. [раздел 5](05-enum-lists.md).

## Вложенные BaseModel

См. [раздел 6](06-nested-models.md).

## Optional[...]

Любой из перечисленных типов может быть обернут в `Optional[T]` - добавляет 1 бит присутствия перед данными поля. См. [раздел 7](07-optional-fields.md).

`Optional[Union[int, str]]` и любой `Union` из более чем одного не-`None` типа - `UnsupportedFieldTypeError`, даже если один из типов внутри union поддерживаемый.

## Вложенность BinaryCallbackData

Поле с аннотацией, у которой уже есть `__bin_plan__` (сам `BinaryCallbackData`), - запрещено, `NestedCallbackDataError`. Использовать обычный `BaseModel` (раздел 6).

Далее: [Enum-поля](04-enum-fields.md).
