# Packing, unpacking, try_unpack

## pack

```python
packed: str = instance.pack()
```

Forms the header (`prefix` + `version`), encodes the fields according to the plan (`__bin_plan__`), passes them through the cipher [(section 12)](12-configuration.md) and the wire codec, returns a string for `callback_data`.

## unpack

```python
restored = SomeCb.unpack(packed)
```

Requires an exact match of `prefix` and `version` with the class it is called on. Mismatch:

| Situation                     | Exception               |
|--------------------------------|---------------------------|
| `prefix` does not match       | `PrefixMismatchError`    |
| `version` does not match      | `VersionMismatchError`   |
| other decoding errors         | `DecodeError`            |

`BinaryCallbackError` exceptions (including `PrefixMismatchError`, `VersionMismatchError`) are propagated as-is, any other error is wrapped in `DecodeError`.

## try_unpack

```python
resolved = BinaryCallbackData.try_unpack(packed, expected=None)
```

Called on `BinaryCallbackData` (not on a specific subclass). Determines the class from the header via the `(prefix, version)` registry (section 11) without knowing the specific type in advance.

| Situation                                          | Result                        |
|------------------------------------------------------|----------------------------------|
| header cannot be read / payload is corrupt            | `None`                          |
| prefix/version not registered                        | `None`                          |
| `expected` is given, the found class does not match   | `None`                          |
| everything matches                                    | instance of the found class      |

`expected` accepts a specific `BinaryCallbackData` class or a `Union` of several such classes. `expected=BinaryCallbackData` (the base class itself) or any type that is not a subclass of `BinaryCallbackData` - `ExpectedTypeError`. Same for any element of a `Union`.

## is_valid / get_header

```python
SomeCb.is_valid(packed)   # bool: header matches the class's prefix/version
SomeCb.get_header(packed)  # BinCbHeader(prefix, version) or None
```

`get_header` decrypts and decodes only the header, without touching the fields. Any error along this path - `None`, no exception is propagated.

Next: [describe](10-describe.md).
