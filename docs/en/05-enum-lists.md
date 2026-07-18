# Enum lists

```python
class Direction(Enum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


path: List[Direction] = bfield(max_len=4)
```

The only supported list type is `List[SomeEnum]`, without `Optional` inside the list. `List[int]`, `List[str]`, `List[Optional[Direction]]` - `UnsupportedFieldTypeError`.

## Parameters

| Parameter   | Required  | Default                                       |
|-------------|-----------|------------------------------------------------|
| `max_len`   | yes       | -, otherwise `MissingMaxLenError`             |
| `bits`      | forbidden | -, passing it - `UnrecognizedBinFieldParamError` |
| `item_bits` | no        | auto from `bin_order`                          |
| `bin_order` | no        | `tuple(EnumCls)`                               |
| `signed`    | forbidden | -, passing it - `UnrecognizedBinFieldParamError` |

`max_len` is the upper bound of the list length, baked into the bit budget regardless of the actual length of a particular instance. The field's size on the wire is fixed and computed from `max_len`, not from the current content.

`bin_order` works the same as for a single enum field (section 4): member order and allowed subset. Duplicates - `DuplicateBinOrderError`.

## item_bits

The width of a single list element in bits. If not passed - computed automatically as the minimum number of bits for `len(bin_order)` values.

If passed explicitly - used instead of the auto-computation, but goes through the same check as `bits` for a single enum: if `2 ** item_bits < len(bin_order)` - `InsufficientBitsError` indicating the actually required number of bits. Passing `item_bits` larger than the minimum is allowed (reserves room for future enum values without changing the format of already-packed data).

## Size formula

```
item_bits = item_bits explicitly, or the minimum bits for len(bin_order) values
len_bits  = the minimum bits for (max_len + 1) values
total     = len_bits + max_len * item_bits
```

`len_bits` is computed over `max_len + 1` length variants (length from `0` to `max_len` inclusive). With `max_len=1` the length takes 2 values, so `len_bits=1`. With `max_len=5` that's 6 values, so `len_bits=3`.

`total` is computed from `max_len`, not the actual length - an empty list and a list of maximum length occupy the same amount of space in the class budget in this field (section 8). A large `max_len` can exceed the budget immediately, even if the actual list is short.

## Encoding

Packing: the list length in `len_bits`, then the index of each element in `bin_order`, in `item_bits`. The order of elements is preserved as-is, repeats are allowed.

An actual length greater than `max_len` - `ListLengthOverflowError` at `pack()` / `encode_fields`. Checked only during encoding: `Model.model_construct(path=[...])` with a length greater than `max_len` is created without error, fails at `pack()`.

## describe

An enum list is described as `[UP,DOWN]` - member names (or values) separated by commas in square brackets. Configurable via `EnumListDescribeOptions` (`as_name`, `separator`, `brackets`) - section 10.

Next: [Nested models](06-nested-models.md).
