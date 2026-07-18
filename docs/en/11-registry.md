# prefix/version registry

A global dictionary `Dict[Tuple[int, int], Type[BinaryCallbackData]]`, keyed by the pair `(prefix, version)`, value - the class. One process - one registry, shared by all subclasses.

## Registration

Happens in `__pydantic_init_subclass__`, at class definition time, before the codec plan is built. An occupied pair `(prefix, version)` with a different class - `PrefixCollisionError`. Re-defining the same class (the same `cls` object) under the same key - not an error.

## resolve

```python
resolve(prefix: int, version: int) -> Optional[Type[BinaryCallbackData]]
```

Returns the registered class or `None` if the pair is not found. Used inside `try_unpack` (section 9) to determine the class from the header without knowing the specific type in advance.

## make_aiogram_prefix

```python
make_aiogram_prefix(prefix: int) -> str
```

Builds the aiogram text prefix using the template `AIOGRAM_PREFIX_TEMPLATE = "bin{prefix}"`. Passed to `CallbackData.__init_subclass__` as the `prefix` argument - used by aiogram filters for routing callback queries, does not affect the binary payload.

## expand_expected_types

```python
expand_expected_types(expected: object) -> Tuple[Type[BinaryCallbackData], ...]
```

Expands the `expected` argument from `try_unpack` into a tuple of classes:

- a single class - a one-element tuple;
- `Union[A, B, ...]` - a tuple of all the union's elements (`get_args`), the `Union` itself is not checked as a single type, each element is checked.

Each element of the result is checked: must be a class (`isinstance(candidate, type)`), a subclass of `BinaryCallbackData`, and not `BinaryCallbackData` itself. Violation of any condition - `ExpectedTypeError` with that element.

## Lifetime

The registry has no method to clear or remove entries - it fills up as modules with class definitions are imported and lives until the process ends.

Next: [Configuration: wire codec and encryption](12-configuration.md).
