# Параметры bfield

Поля объявляются через `bfield(...)` вместо `Field(...)`:

```python
value: int = bfield(bits=8, signed=False)
```

## Сигнатура

```python
bfield(
    bits=None,
    item_bits=None,
    bin_order=None,
    signed=None,
    max_len=None,
    default=PydanticUndefined,
    default_factory=None,
)
```

## Применимость по типам

| Параметр    | bool | int             | Enum       | List[Enum]        | вложенная модель |
|-------------|------|-----------------|------------|-------------------|------------------|
| `bits`      | нет  | опционален (32) | обязателен | нет               | нет              |
| `item_bits` | нет  | нет             | нет        | опционален (авто) | нет              |
| `bin_order` | нет  | нет             | опционален | опционален        | нет              |
| `signed`    | нет  | обязателен      | нет        | нет               | нет              |
| `max_len`   | нет  | нет             | нет        | нет               | нет              |

"нет" - передача значения (в т.ч. `False`) вызывает `UnrecognizedBinFieldParamError`.

Если поле объявлено без `bfield` (обычным `Field` или без значения по умолчанию), `json_schema_extra` пуст, и для большинства типов это дает ошибки обязательных параметров (`MissingSignedError`, `MissingBitsError`, `MissingMaxLenError`) - кроме `bool`, где все параметры необязательны.

`default` / `default_factory` работают как в обычном pydantic `Field`.

Внутри `bfield` параметры кладутся в `json_schema_extra` под ключами `bin_bits`, `bin_item_bits`, `bin_order`, `bin_signed`, `bin_max_len`. План кодека (`build_codec_plan`) читает их оттуда.

Далее: [Типы полей](03-field-types.md).
