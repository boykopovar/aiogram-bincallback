# Определение callback-класса

```python
class SomeCb(BinaryCallbackData, prefix=1, version=1):
    ...
```

`prefix` и `version` - обязательные именованные аргументы `__init_subclass__`.

| Параметр  | Тип   | Обязателен | Хранится в            |
|-----------|-------|------------|-----------------------|
| `prefix`  | `int` | да         | `cls.__bin_prefix__`  |
| `version` | `int` | да         | `cls.__bin_version__` |

`prefix=None` - `TypeError` в момент определения класса, до pydantic-валидации.

Прямое наследование от `BinaryCallbackData` без `prefix`/`version` не производится - это базовый класс, `__bin_prefix__ is None`, вызов `is_valid`/`describe` на нем - `TypeError`.

`prefix` транслируется в текстовый префикс aiogram `bin{prefix}` (например, при `prefix=1` получается `"bin1"`). Используется aiogram для маршрутизации фильтров, на бинарный payload не влияет.

## Регистрация

При определении подкласса (`__pydantic_init_subclass__`) класс регистрируется в глобальном реестре по паре `(prefix, version)`. Занятая пара - `PrefixCollisionError`. Регистрация нужна для `try_unpack` (раздел 9, реестр - раздел 11).

В момент определения класса также строится план кодека (`__bin_plan__`) и проверяется бюджет бит [(раздел 8)](08-size-limit.md). Ошибка в структуре полей проявляется при импорте модуля, не при `pack()`.

Далее: [Параметры bfield](02-bfield-parameters.md).
