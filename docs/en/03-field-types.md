# Field types

Supported annotations: `bool`, `int`, subclasses of `Enum`, `List[EnumT]`, nested `BaseModel`, any of these wrapped in `Optional[...]`.

Any other annotation (`str`, `float`, `List[int]`, `List[Optional[Enum]]`, `Union[int, str]`) - `UnsupportedFieldTypeError` when the codec plan is built.

## bool

```python
flag: bool = bfield()
```

- exactly 1 bit (`DEFAULT_BOOL_BITS`);
- does not accept any `bfield()` parameters other than `default`/`default_factory` - passing `bits`, `item_bits`, `bin_order`, `signed` or `max_len` (including `False`) raises `UnrecognizedBinFieldParamError`;
- encoded as `int(value)`, decoded via `bool(...)`.

## int

```python
value: int = bfield(bits=16, signed=False)
```

| Parameter | Required | Default |
|-----------|----------|---------|
| `signed`  | yes      | -       |
| `bits`    | no       | 32      |

`item_bits`, `bin_order`, `max_len` are forbidden for an `int` field - passing any of them raises `UnrecognizedBinFieldParamError`.

Bounds: with `signed=True` the range is `-(2**(bits-1))` .. `2**(bits-1)-1`, with `signed=False` the range is `0` .. `2**bits-1`.

Out-of-range values are not detected at class definition time or when the pydantic model is created - only at `pack()` / `encode_fields`, the result is `ValueOverflowError`. Boundary values pass without error.

## Enum

See [section 4](04-enum-fields.md).

## List[Enum]

See [section 5](05-enum-lists.md).

## Nested BaseModel

See [section 6](06-nested-models.md).

## Optional[...]

Any of the listed types can be wrapped in `Optional[T]` - adds 1 presence bit before the field's data. See [section 7](07-optional-fields.md).

`Optional[Union[int, str]]` and any `Union` of more than one non-`None` type - `UnsupportedFieldTypeError`, even if one of the types inside the union is supported.

## Nesting of BinaryCallbackData

A field with an annotation that already has `__bin_plan__` (`BinaryCallbackData` itself) - forbidden, `NestedCallbackDataError`. Use a plain `BaseModel` instead (section 6).

Next: [Enum fields](04-enum-fields.md).
