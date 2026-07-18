# bfield parameters

Fields are declared via `bfield(...)` instead of `Field(...)`:

```python
value: int = bfield(bits=8, signed=False)
```

## Signature

```python
bfield(
    bits=None,
    item_bits=None,
    bin_order=None,
    signed=None,
    max_len=None,
    default=PydanticUndefined,
    default_factory=None,
)
```

## Applicability by type

| Parameter   | bool | int             | Enum       | List[Enum]        | nested model |
|-------------|------|-----------------|------------|--------------------|--------------|
| `bits`      | no   | optional (32)   | required   | no                 | no           |
| `item_bits` | no   | no              | no         | optional (auto)    | no           |
| `bin_order` | no   | no              | optional   | optional           | no           |
| `signed`    | no   | required        | no         | no                 | no           |
| `max_len`   | no   | no              | no         | no                 | no           |

"no" - passing a value (including `False`) raises `UnrecognizedBinFieldParamError`.

If a field is declared without `bfield` (a plain `Field` or no default value), `json_schema_extra` is empty, and for most types this produces required-parameter errors (`MissingSignedError`, `MissingBitsError`, `MissingMaxLenError`) - except for `bool`, where all parameters are optional.

`default` / `default_factory` work as in a regular pydantic `Field`.

Inside `bfield` the parameters are placed into `json_schema_extra` under the keys `bin_bits`, `bin_item_bits`, `bin_order`, `bin_signed`, `bin_max_len`. The codec plan (`build_codec_plan`) reads them from there.

Next: [Field types](03-field-types.md).
