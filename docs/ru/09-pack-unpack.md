# Упаковка, распаковка, try_unpack

## pack

```python
packed: str = instance.pack()
```

Формирует заголовок (`prefix` + `version`), кодирует поля по плану (`__bin_plan__`), пропускает через шифр [(раздел 12)](12-configuration.md) и wire codec, возвращает строку для `callback_data`.

## unpack

```python
restored = SomeCb.unpack(packed)
```

Требует точное совпадение `prefix` и `version` с классом, на котором вызван. Несовпадение:

| Ситуация                    | Исключение             |
|-----------------------------|------------------------|
| `prefix` не совпадает       | `PrefixMismatchError`  |
| `version` не совпадает      | `VersionMismatchError` |
| прочие ошибки декодирования | `DecodeError`          |

Исключения `BinaryCallbackError` (включая `PrefixMismatchError`, `VersionMismatchError`) пробрасываются как есть, любая прочая ошибка оборачивается в `DecodeError`.

## try_unpack

```python
resolved = BinaryCallbackData.try_unpack(packed, expected=None)
```

Вызывается на `BinaryCallbackData` (не на конкретном подклассе). Определяет класс по заголовку через реестр `(prefix, version)` (раздел 11) без знания конкретного типа заранее.

| Ситуация                                        | Результат            |
|---------------------------------------------------|------------------------|
| заголовок не читается / payload битый              | `None`                 |
| prefix/version не зарегистрированы                 | `None`                 |
| `expected` задан, найденный класс не подходит      | `None`                 |
| все совпало                                        | экземпляр найденного класса |

`expected` принимает конкретный класс `BinaryCallbackData` или `Union` из нескольких таких классов. `expected=BinaryCallbackData` (сам базовый класс) или любой тип, не являющийся подклассом `BinaryCallbackData`, - `ExpectedTypeError`. То же для любого элемента `Union`.

## is_valid / get_header

```python
SomeCb.is_valid(packed)   # bool: заголовок совпадает с prefix/version класса
SomeCb.get_header(packed)  # BinCbHeader(prefix, version) или None
```

`get_header` расшифровывает и декодирует только заголовок, не трогая поля. Любая ошибка на этом пути - `None`, исключение не пробрасывается.

Далее: [describe](10-describe.md).
