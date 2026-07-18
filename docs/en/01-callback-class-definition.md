# Callback class definition

```python
class SomeCb(BinaryCallbackData, prefix=1, version=1):
    ...
```

`prefix` and `version` are required keyword arguments of `__init_subclass__`.

| Parameter | Type  | Required | Stored in              |
|-----------|-------|----------|-------------------------|
| `prefix`  | `int` | yes      | `cls.__bin_prefix__`   |
| `version` | `int` | yes      | `cls.__bin_version__`  |

`prefix=None` - `TypeError` at class definition time, before pydantic validation.

Direct inheritance from `BinaryCallbackData` without `prefix`/`version` is not performed - it is the base class, `__bin_prefix__ is None`, calling `is_valid`/`describe` on it - `TypeError`.

`prefix` is translated into the aiogram text prefix `bin{prefix}` (for example, `prefix=1` gives `"bin1"`). Used by aiogram for filter routing, does not affect the binary payload.

## Registration

When a subclass is defined (`__pydantic_init_subclass__`), the class is registered in the global registry under the pair `(prefix, version)`. An occupied pair - `PrefixCollisionError`. Registration is required for `try_unpack` (section 9, registry - section 11).

At class definition time the codec plan (`__bin_plan__`) is also built and the bit budget is checked [(section 8)](08-size-limit.md). An error in the field structure surfaces when the module is imported, not at `pack()`.

Next: [bfield parameters](02-bfield-parameters.md).
