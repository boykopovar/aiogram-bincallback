# Реестр prefix/version

Глобальный словарь `Dict[Tuple[int, int], Type[BinaryCallbackData]]`, ключ - пара `(prefix, version)`, значение - класс. Один процесс - один реестр, общий для всех подклассов.

## Регистрация

Происходит в `__pydantic_init_subclass__`, при определении класса, до построения плана кодека. Занятая пара `(prefix, version)` с другим классом - `PrefixCollisionError`. Повторное определение того же класса (тот же объект `cls`) под тем же ключом - не ошибка.

## resolve

```python
resolve(prefix: int, version: int) -> Optional[Type[BinaryCallbackData]]
```

Возвращает зарегистрированный класс или `None`, если пара не найдена. Используется внутри `try_unpack` (раздел 9) для определения класса по заголовку без знания конкретного типа заранее.

## make_aiogram_prefix

```python
make_aiogram_prefix(prefix: int) -> str
```

Строит текстовый префикс aiogram по шаблону `AIOGRAM_PREFIX_TEMPLATE = "bin{prefix}"`. Передается в `CallbackData.__init_subclass__` как аргумент `prefix` - используется aiogram-фильтрами для маршрутизации callback-запросов, на бинарный payload не влияет.

## expand_expected_types

```python
expand_expected_types(expected: object) -> Tuple[Type[BinaryCallbackData], ...]
```

Разворачивает аргумент `expected` из `try_unpack` в кортеж классов:

- одиночный класс - кортеж из одного элемента;
- `Union[A, B, ...]` - кортеж всех элементов union (`get_args`), сам `Union` не проверяется как единый тип, проверяется каждый элемент.

Каждый элемент результата проверяется: должен быть классом (`isinstance(candidate, type)`), подклассом `BinaryCallbackData`, и не самим `BinaryCallbackData`. Нарушение любого условия - `ExpectedTypeError` с этим элементом.

## Время жизни

Реестр не имеет метода очистки или удаления записей - заполняется при импорте модулей с определениями классов и живет до завершения процесса.

Далее: [Конфигурация: wire codec и шифрование](12-configuration.md).
