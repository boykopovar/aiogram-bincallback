# Exceptions

Root of the hierarchy - `BinaryCallbackError(ValueError)`. All library exceptions are its subclasses, except `PrefixEnumMismatchError`, which inherits from `BinaryCallbackError` directly outside the branches below.

## Hierarchy

```
BinaryCallbackError
├── DefinitionError
│   ├── UnsupportedFieldTypeError
│   ├── MissingBitsError
│   ├── InsufficientBitsError
│   ├── DuplicateBinOrderError
│   ├── MissingMaxLenError
│   ├── UnrecognizedBinFieldParamError
│   ├── MissingSignedError
│   ├── NestedCallbackDataError
│   ├── CircularNestingError
│   ├── SizeLimitExceededError
│   ├── PrefixCollisionError
│   └── ExpectedTypeError
├── EncodeError
│   ├── ValueOverflowError
│   └── ListLengthOverflowError
├── DecodeError
│   ├── PrefixMismatchError
│   ├── VersionMismatchError
│   ├── PayloadCorruptError
│   └── DecryptionError
├── PrefixEnumMismatchError
└── CipherReconfiguredAfterUseError
```

## DefinitionError - errors at class definition time

| Class                              | When it occurs                                                                                                                                                 |
|--------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `UnsupportedFieldTypeError`         | the field annotation is not among the supported set of types (section 3)                                                                                      |
| `MissingBitsError`                  | an `int` field without the required `bits`                                                                                                                     |
| `InsufficientBitsError`             | `bits`/`item_bits` of an enum field is less than the minimum for `len(bin_order)` values                                                                       |
| `DuplicateBinOrderError`            | a repeated enum member in `bin_order`                                                                                                                          |
| `MissingMaxLenError`                | a `List[Enum]` field without the required `max_len`                                                                                                            |
| `UnrecognizedBinFieldParamError`    | an argument was passed to `bfield()` for a field that is not among the ones allowed for that field's type (e.g. `bits` for `List[Enum]`, `signed` for `bool`, `Enum`, `List[Enum]` or a nested model) |
| `MissingSignedError`                | an `int` field without the required `signed`                                                                                                                   |
| `NestedCallbackDataError`           | a field references a `BinaryCallbackData` subclass instead of a plain `BaseModel`                                                                              |
| `CircularNestingError`              | a nested model references itself directly or through several levels                                                                                            |
| `SizeLimitExceededError`            | the class's total bit budget exceeds `MAX_PAYLOAD_BITS`                                                                                                        |
| `PrefixCollisionError`              | the pair `(prefix, version)` is already occupied by another class in the registry                                                                              |
| `ExpectedTypeError`                 | an element of `expected` in `try_unpack` is not a subclass of `BinaryCallbackData` or is `BinaryCallbackData` itself                                            |

All `DefinitionError` surface when the module with the class definition is imported (`__pydantic_init_subclass__`), except `ExpectedTypeError`, which occurs when `try_unpack` is called.

## EncodeError - errors during packing

| Class                      | When it occurs                                                              |
|------------------------------|--------------------------------------------------------------------------------|
| `ValueOverflowError`        | the value of an `int` field is out of the bounds set by `bits` and `signed`   |
| `ListLengthOverflowError`   | the actual length of a `List[Enum]` field is greater than `max_len`           |

Both are checked only at `pack()` / `encode_fields`, not when the pydantic model is created.

## DecodeError - errors during unpacking

| Class                    | When it occurs                                                                     |
|----------------------------|-----------------------------------------------------------------------------------|
| `PrefixMismatchError`     | the decoded `prefix` does not match the `prefix` of the class `unpack` was called on |
| `VersionMismatchError`    | the decoded `version` does not match the class's `version`                         |
| `PayloadCorruptError`     | a character outside the base128 alphabet, a missing or corrupted length marker bit  |
| `DecryptionError`         | an error on the side of a custom `ICipher.decrypt` implementation                   |

Any other error inside `unpack` that is not a `BinaryCallbackError` is wrapped in `DecodeError` with the text of the original exception.

## Other

| Class                                | When it occurs                                                                                                                    |
|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| `PrefixEnumMismatchError`              | in `describe(prefix_enum=...)` there is no member with `value == prefix`                                                             |
| `CipherReconfiguredAfterUseError`      | a repeated `configure(cipher=...)` with a different cipher object after the previous one was already used in `pack`/`unpack`/`get_header` |

## try_unpack and is_valid do not raise exceptions

`try_unpack` returns `None` instead of raising an exception on an unreadable header, an unregistered `(prefix, version)` pair, or a mismatch with `expected` - except for the case of an invalid `expected` itself, in which case `ExpectedTypeError` is raised. `is_valid` and `get_header` return `False`/`None` on any decoding error, they do not propagate anything.
