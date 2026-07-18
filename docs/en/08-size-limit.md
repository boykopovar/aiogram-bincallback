# Bit budget and size limit

## Constants

| Constant           | Value | Meaning                                             |
|---------------------|------:|-------------------------------------------------------|
| `HEADER_BITS`       |    24 | header size (prefix + version)                        |
| `PREFIX_BITS`       |    16 | width of the prefix field in the header                |
| `VERSION_BITS`      |     8 | width of the version field in the header                |
| `MAX_TOTAL_BITS`    |   440 | header + payload, computed from the Telegram limit      |
| `MAX_PAYLOAD_BITS`  |   416 | `MAX_TOTAL_BITS - HEADER_BITS`, available for fields    |

`MAX_TOTAL_BITS` is derived from `MAX_CALLBACK_LENGTH = 64` characters of the base128 alphabet, rounded down to a multiple of 8 bits. Available as `BinaryCallbackData.max_total_bits()` / `.max_payload_bits()` - the same for all subclasses.

## Check at class definition time

The sum of bits of all fields in the plan (`plan_total_bits`, recursively through nested models) is compared with `MAX_PAYLOAD_BITS` at class definition time (`__pydantic_init_subclass__`). Exceeding it - `SizeLimitExceededError` indicating the actual and allowed number of bits. A value exactly on the boundary (`== MAX_PAYLOAD_BITS`) passes without error.

## What is included in the sum

| Field type       | Contribution to the budget                |
|-------------------|----------------------------------------------|
| `bool`             | 1                                            |
| `int`              | `bits` (or 32 by default)                    |
| `Enum`             | `bits`                                       |
| `List[Enum]`       | `len_bits + max_len * item_bits`             |
| nested model       | sum of bits of all its fields, recursively   |
| `Optional[...]`    | +1 to the base type's contribution (presence bit) |

Next: [Packing, unpacking, try_unpack](09-pack-unpack.md).
