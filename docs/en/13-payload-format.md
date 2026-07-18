# Payload format at the bit level

The final bytes before `cipher.encrypt` and `wire_codec.encode` are a continuous bit stream with no alignment between individual fields. Byte alignment is applied once, at the end, when converting the accumulated bits to `bytes`.

## Byte order

All integers are written and read as big-endian, bit by bit, via `BitWriter` / `BitReader` (`bitstream.py`). Writing - shifting the accumulator left by `bits` and adding the value in the low-order bits. Reading - extracting `bits` bits from the current position, counted from the start of the stream.

## Header

The first `HEADER_BITS = 24` bits of the payload:

| Field     | Position (bits from the start) | Width               |
|-----------|----------------------------------|----------------------|
| `prefix`  | 0..15                             | `PREFIX_BITS = 16`  |
| `version` | 16..23                            | `VERSION_BITS = 8`  |

Both fields are unsigned. Encoded by `encode_header`, decoded by `decode_header`, independent of the specific class's plan.

## Body: field order

After the header, fields follow in declaration order in the class (the order of the `CodecPlan`, built from the pydantic model's annotations). Order is not sorted by name and does not depend on `default`/`default_factory`.

## Encoding by type

| Type              | What is written to the wire                                                            |
|--------------------|-------------------------------------------------------------------------------------------|
| `bool`             | 1 bit: `int(value)`                                                                      |
| `int`              | `bits` bits, `write_uint` (unsigned) or `write_int` (signed, two's complement)          |
| `Enum`             | `bits` bits, unsigned: `bin_order.index(value)`                                          |
| `List[Enum]`       | `len_bits` bits of length (unsigned), then `item_bits` bits per element in order          |
| nested model       | the nested model's fields continue the same stream, no header and no alignment            |
| `Optional[T]`      | 1 presence bit before the data; if `0` the data of `T` is entirely absent from the wire    |

## Signed integers

`signed=True` uses two's complement (`_signed_to_unsigned` / `_unsigned_to_signed`) within the width of `bits`: the high bit is the sign bit. The value `-1` with `bits=8` is written as `0b11111111`.

## Trailing alignment

`BitWriter.to_bytes()` appends 0 to 7 zero bits to the end of the stream so the length becomes a multiple of 8, then converts to `bytes`. These zero bits are not read during `decode_fields` - the read position (`reader.position_bits`) stops at the last actually written bit of the last field.

## Layout example

A class with `prefix=1, version=1` and fields `flag: bool`, `value: int = bfield(bits=8, signed=False)`:

```
bits 0..15   - prefix (16 bits)
bits 16..23  - version (8 bits)
bit  24      - flag (1 bit)
bits 25..32  - value (8 bits)
bits 33..39  - zero padding to the byte boundary
```

Next: [Exception reference](14-exceptions.md).
