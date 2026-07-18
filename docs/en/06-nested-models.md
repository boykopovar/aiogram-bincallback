# Nested models

A field can reference a plain `pydantic.BaseModel` (not `BinaryCallbackData`):

```python
class GpsPosition(BaseModel):
    latitude: int = bfield(bits=32, signed=True)
    longitude: int = bfield(bits=32, signed=True)


class DeviceLocationCb(BinaryCallbackData, prefix=1, version=1):
    device_id: int = bfield(bits=8, signed=False)
    position: GpsPosition
```

## Rules

- a model field does not accept `bits`, `item_bits`, `bin_order`, `max_len`, `signed` - these parameters belong to the fields inside the nested model, passing any of them - `UnrecognizedBinFieldParamError`;
- the nested model is not aligned to a byte as a separate block - its fields continue the same bit stream of the parent (section 13);
- field paths inside are formed with a dot: `position.latitude`, `position.longitude` - used in error messages;
- the same model can be used in several parents or twice in one (`first: Shared`, `second: Shared`) - each usage builds an independent codec plan, no name conflicts occur.

## Bit counting

The size of a nested model is the sum of the sizes of all its fields, recursively. Counted in the class budget (section 8) and when adding the presence bit for `Optional[Inner]` (section 7).

## Circular references

Direct (`Node.child: Node`) or indirect recursion through several levels (`A.b: B`, `B.a: A`) - `CircularNestingError` indicating the field path and the name of the re-referenced model.

## BinaryCallbackData nesting is forbidden

An annotation with an already-built `__bin_plan__` (`BinaryCallbackData` itself) - `NestedCallbackDataError`. `BinaryCallbackData` has its own header (`prefix`/`version`) and registration in the registry - nesting one packed format inside another is not supported.

Next: [Optional fields](07-optional-fields.md).
