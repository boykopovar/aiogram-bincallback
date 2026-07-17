# describe

```python
text: str = instance.describe()
```

Вызывается на экземпляре подкласса `BinaryCallbackData`. Вызов на самом `BinaryCallbackData` - `TypeError`.

Возвращает строку из токенов, разделенных `DESCRIBE_FIELD_SEPARATOR` (`:`). Первый токен - prefix, остальные - значения полей плана в порядке объявления.

## Сигнатура

```python
def describe(
    self,
    prefix_enum=None,
    bool_as_int=True,
    enum_as_name=True,
    enum_list_as_name=True,
    enum_list_separator=',',
    enum_list_brackets=True,
) -> str:
```

## prefix_enum

Не задан (`None`) - первый токен - `str(prefix)`, десятичное число.

Задан - `Enum`, у которого `member.value == prefix`, - первый токен - имя члена (`member.name`). Совпадение не найдено - `PrefixEnumMismatchError`.

## bool_as_int

`True` - значение `bool`-поля - `"0"` или `"1"`. `False` - `"True"` / `"False"` (`str(value)`).

## enum_as_name

`True` - значение одиночного enum-поля - `member.name`. `False` - `str(member.value)`.

## enum_list_as_name / enum_list_separator / enum_list_brackets

Управляют форматированием `List[Enum]`-полей, объединены в `EnumListDescribeOptions(as_name, separator, brackets)`.

`as_name` - то же самое для каждого элемента списка, что `enum_as_name` для одиночного enum. `separator` - строка между элементами внутри списка. `brackets` - оборачивать ли результат в `[` и `]`.

Пример: список из `Direction.UP, Direction.LEFT` при `as_name=True, separator=",", brackets=True` - `[UP,LEFT]`.

## None-значения

Поле со значением `None` (пустой `Optional`) - токен `"None"` (`str(None)`), остальные опции форматирования для этого поля не применяются.

## Вложенные модели

Токен вложенной модели - токены ее собственных полей, рекурсивно, объединенные тем же `DESCRIBE_FIELD_SEPARATOR`, без отдельных скобок вокруг вложенной группы.

Далее: [Реестр prefix/version](11-registry.md).
