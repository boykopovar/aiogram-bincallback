# Вложенные модели

Поле может ссылаться на обычный `pydantic.BaseModel` (не `BinaryCallbackData`):

```python
class GpsPosition(BaseModel):
    latitude: int = bfield(bits=32, signed=True)
    longitude: int = bfield(bits=32, signed=True)


class DeviceLocationCb(BinaryCallbackData, prefix=1, version=1):
    device_id: int = bfield(bits=8, signed=False)
    position: GpsPosition
```

## Правила

- поле-модель не принимает `bits`, `bin_order`, `max_len` - эти параметры относятся к полям внутри вложенной модели;
- `signed` для вложенной модели - `SignedNotApplicableError`;
- вложенная модель не выравнивается по байту отдельным блоком - ее поля продолжают тот же битовый поток родителя (раздел 13);
- пути полей внутри формируются через точку: `position.latitude`, `position.longitude` - используются в сообщениях об ошибках;
- одна и та же модель может использоваться в нескольких родителях или дважды в одном (`first: Shared`, `second: Shared`) - каждое использование строит независимый план кодека, конфликтов имен не возникает.

## Подсчет бит

Размер вложенной модели - сумма размеров всех ее полей, рекурсивно. Учитывается в бюджете класса (раздел 8) и при добавлении presence-бита для `Optional[Inner]` (раздел 7).

## Циклические ссылки

Прямая (`Node.child: Node`) или опосредованная через несколько уровней (`A.b: B`, `B.a: A`) рекурсия - `CircularNestingError` с указанием пути поля и имени модели повторной ссылки.

## Запрет на BinaryCallbackData внутри

Аннотация с уже построенным `__bin_plan__` (сам `BinaryCallbackData`) - `NestedCallbackDataError`. У `BinaryCallbackData` есть собственный заголовок (`prefix`/`version`) и регистрация в реестре - вложение одного пакованного формата в другой не поддерживается.

Далее: [Optional-поля](07-optional-fields.md).
