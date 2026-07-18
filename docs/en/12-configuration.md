# Configuration: wire codec and encryption

Two global, interchangeable components: `IWireCodec` (translation of bytes to a callback_data string and back) and `ICipher` (encryption of the payload before the wire codec). Configured with the `configure()` function.

## configure

```python
def configure(*, wire_codec: Optional[IWireCodec] = None, cipher: Optional[ICipher] = None) -> None:
```

Both parameters are keyword-only and optional. `None` - the corresponding component is not changed. Defaults before the first call to `configure()`: `Base128WireCodec()` and `NullCipher()`.

## IWireCodec

```python
class IWireCodec(ABC):
    def encode(self, data: bytes) -> str: ...
    def decode(self, packed: str) -> bytes: ...
```

`encode` translates the encrypted bytes (header + payload) into a string for `callback_data`. `decode` is the reverse operation.

## Base128WireCodec

The only built-in `IWireCodec` implementation. Encodes bytes as a base-128 number (`BASE128_RADIX`, alphabet - all characters with codes `0..127`), with a length marker bit before the conversion: `marker = 1 << (len(data) * 8)`, `value = marker | int(data)`. The marker preserves the leading zero bytes of the original data, which would otherwise be lost when converting to a number.

`decode` restores the data length from the bit length of the marker in the decoded number. A character outside the alphabet during `decode` - `PayloadCorruptError`. A value without the marker bit (`value == 0` after reading) or a marker not on a byte boundary - `PayloadCorruptError`.

`MAX_TOTAL_BITS` and `MAX_PAYLOAD_BITS` [(section 8)](08-size-limit.md) are computed for this codec and the `MAX_CALLBACK_LENGTH = 64` character limit - replacing `wire_codec` with an implementation with a different encoding density does not automatically recompute these constants.

## ICipher

```python
class ICipher(ABC):
    def encrypt(self, data: bytes) -> bytes: ...
    def decrypt(self, data: bytes) -> bytes: ...
```

Applied to the header and payload bytes together, before `wire_codec.encode`. A custom implementation is plugged in via `configure(cipher=...)`.

## NullCipher

The default built-in `ICipher` implementation. `encrypt` and `decrypt` return the input bytes unchanged - encryption is effectively absent until another `cipher` is set.

## Protection against changing the cipher "on the fly"

The module tracks the `_cipher_used` flag, set to `True` on every call to `get_cipher()` (i.e. on every `pack()`/`unpack()`/`get_header()`). A repeated call to `configure(cipher=...)` with a different cipher object after the previous one has already been used - `CipherReconfiguredAfterUseError`. The same cipher object (`cipher is _cipher`) can be passed again without error. `wire_codec` has no such protection, it can be changed freely at any time.

Next: [Payload format at the bit level](13-payload-format.md).
