# Конфигурация: wire codec и шифрование

Два глобальных, взаимозаменяемых компонента: `IWireCodec` (перевод байт в строку callback_data и обратно) и `ICipher` (шифрование payload перед wire codec). Настраиваются функцией `configure()`.

## configure

```python
def configure(*, wire_codec: Optional[IWireCodec] = None, cipher: Optional[ICipher] = None) -> None:
```

Оба параметра именованные и необязательные. `None` - соответствующий компонент не меняется. Значения по умолчанию до первого вызова `configure()`: `Base128WireCodec()` и `NullCipher()`.

## IWireCodec

```python
class IWireCodec(ABC):
    def encode(self, data: bytes) -> str: ...
    def decode(self, packed: str) -> bytes: ...
```

`encode` переводит зашифрованные байты (заголовок + payload) в строку для `callback_data`. `decode` - обратная операция.

## Base128WireCodec

Единственная встроенная реализация `IWireCodec`. Кодирует байты как число по основанию 128 (`BASE128_RADIX`, алфавит - все символы с кодами `0..127`), с battой-маркером длины перед конвертацией: `marker = 1 << (len(data) * 8)`, `value = marker | int(data)`. Маркер сохраняет ведущие нулевые байты исходных данных, которые иначе терялись бы при переводе в число.

`decode` восстанавливает длину данных по битовой длине маркера в декодированном числе. Символ вне алфавита при `decode` - `PayloadCorruptError`. Значение без бита-маркера (`value == 0` после чтения) или маркер не на границе байта - `PayloadCorruptError`.

`MAX_TOTAL_BITS` и `MAX_PAYLOAD_BITS` [(раздел 8)](08-size-limit.md) вычислены под этот кодек и лимит `MAX_CALLBACK_LENGTH = 64` символа - замена `wire_codec` на реализацию с другой плотностью кодирования не пересчитывает эти константы автоматически.

## ICipher

```python
class ICipher(ABC):
    def encrypt(self, data: bytes) -> bytes: ...
    def decrypt(self, data: bytes) -> bytes: ...
```

Применяется к байтам заголовка и payload вместе, до `wire_codec.encode`. Пользовательская реализация подключается через `configure(cipher=...)`.

## NullCipher

Встроенная реализация `ICipher` по умолчанию. `encrypt` и `decrypt` возвращают входные байты без изменений - шифрование фактически отсутствует, пока не задан другой `cipher`.

## Защита от смены шифра "на лету"

Модуль отслеживает флаг `_cipher_used`, устанавливаемый в `True` при каждом вызове `get_cipher()` (то есть при каждом `pack()`/`unpack()`/`get_header()`). Повторный вызов `configure(cipher=...)` с другим объектом шифра после того, как предыдущий уже использовался, - `CipherReconfiguredAfterUseError`. Тот же самый объект шифра (`cipher is _cipher`) можно передать повторно без ошибки. `wire_codec` такой защиты не имеет, меняется свободно в любой момент.

Далее: [Формат payload на уровне бит](13-payload-format.md).
