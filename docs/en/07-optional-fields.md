# Optional fields

Any supported type (`bool`, `int`, `Enum`, `List[Enum]`, nested model) can be wrapped in `Optional[T]`.

```python
value: Optional[int] = bfield(bits=16, signed=False)
```

## Rules

- adds exactly 1 presence bit before the field's data (`DEFAULT_BOOL_BITS`);
- when packing: if the value is `None`, `0` is written and the field's data is skipped entirely; if not `None`, `1` is written followed by the field's data in the regular format;
- when unpacking: the presence bit is read first, if `0` the field's value is `None`, further bits of this field are not read;
- for a nested model there is one presence bit for the entire model - if `None` the whole bit tail of the nested fields is not consumed;
- nested `Optional` fields inside an `Optional` model are counted independently, each with its own presence bit.

## Bit budget

The presence bit is always counted in the overall class budget [(section 8)](08-size-limit.md) (if `Optional`), regardless of whether a particular instance will actually have a `None` value.

## Type restriction

`Optional[Union[int, str]]` and any `Union` of more than one non-`None` type - `UnsupportedFieldTypeError`, even if one of the union's types is supported.

Next: [Bit budget and size limit](08-size-limit.md).
