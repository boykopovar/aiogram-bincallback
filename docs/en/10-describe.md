# describe

```python
text: str = instance.describe()
```

Called on an instance of a `BinaryCallbackData` subclass. Calling it on `BinaryCallbackData` itself - `TypeError`.

Returns a string of tokens separated by `DESCRIBE_FIELD_SEPARATOR` (`:`). The first token is the prefix, the rest are the values of the plan's fields in declaration order.

## Signature

```python
def describe(
    self,
    prefix_enum=None,
    bool_as_int=True,
    enum_as_name=True,
    enum_list_as_name=True,
    enum_list_separator=',',
    enum_list_brackets=True,
) -> str:
```

## prefix_enum

Not set (`None`) - the first token is `str(prefix)`, a decimal number.

Set - an `Enum` where `member.value == prefix` - the first token is the member's name (`member.name`). No match found - `PrefixEnumMismatchError`.

## bool_as_int

`True` - the value of a `bool` field is `"0"` or `"1"`. `False` - `"True"` / `"False"` (`str(value)`).

## enum_as_name

`True` - the value of a single enum field is `member.name`. `False` - `str(member.value)`.

## enum_list_as_name / enum_list_separator / enum_list_brackets

Control the formatting of `List[Enum]` fields, combined into `EnumListDescribeOptions(as_name, separator, brackets)`.

`as_name` - the same thing for each list element as `enum_as_name` for a single enum. `separator` - the string between elements inside the list. `brackets` - whether to wrap the result in `[` and `]`.

Example: a list of `Direction.UP, Direction.LEFT` with `as_name=True, separator=",", brackets=True` - `[UP,LEFT]`.

## None values

A field with a `None` value (an empty `Optional`) - the token `"None"` (`str(None)`), the rest of the formatting options for this field do not apply.

## Nested models

The token of a nested model is the tokens of its own fields, recursively, joined by the same `DESCRIBE_FIELD_SEPARATOR`, without separate brackets around the nested group.

Next: [prefix/version registry](11-registry.md).
