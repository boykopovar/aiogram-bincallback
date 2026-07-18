# Enum fields

```python
class Status(str, Enum):
    PENDING = "pending"
    SHIPPED = "shipped"


status: Status = bfield(bits=4)
```

Any subclass of `Enum` is supported (`Enum`, `IntEnum`, `str`-based `Enum`). The type of the members does not matter - the positional index of the member in `bin_order` is transmitted on the wire, not the value itself.

## bits

Required, otherwise `MissingBitsError`.

Minimum bits = `ceil(log2(len(bin_order)))`, no less than 1 when there is more than one member. If `2 ** bits < len(bin_order)` - `InsufficientBitsError` indicating the required number of bits.

Special case: an enum with a single member allows `bits=0`, the field occupies no bits on the wire. A negative `bits` for a single member still gives `InsufficientBitsError` (`2 ** bits < 1`).

## bin_order

Optional. Sets:

1. the encoding order of members into bits (index in the tuple = the recorded number);
2. the allowed subset of members for this field.

If not passed - `tuple(EnumCls)` (declaration order). Can be a strict subset of all members - the rest require fewer bits and do not participate in encoding.

A duplicate member in `bin_order` - `DuplicateBinOrderError`.

## signed, item_bits, max_len

Not applicable. Passing any of them (including `signed=False`) - `UnrecognizedBinFieldParamError`.

## Encoding

Packing: `bin_order.index(value)`, written in `bits` bits as unsigned. Unpacking: the index is read and turned into `bin_order[index]`.

A value outside `bin_order` during `pack()` - `bin_order.index(value)` raises `ValueError` (not wrapped in the library's own exception).

Next: [Enum lists](05-enum-lists.md).
