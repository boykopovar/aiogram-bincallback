from typing import Optional
from typing import Sequence
from typing import Tuple


class BinaryCallbackError(ValueError):
    pass


class DefinitionError(BinaryCallbackError):
    pass


class UnsupportedFieldTypeError(DefinitionError):
    def __init__(self, path: str, annotation: object) -> None:
        super().__init__(f"field '{path}' has unsupported type {annotation!r}")


class MissingBitsError(DefinitionError):
    def __init__(self, path: str) -> None:
        super().__init__(f"field '{path}' requires an explicit bits= argument to bfield()")


class InsufficientBitsError(DefinitionError):
    def __init__(self, path: str, bits: int, required_bits: int) -> None:
        super().__init__(
            f"enum field '{path}' reserves {bits} bits, "
            f"but its bin_order needs at least {required_bits} bits"
        )


class DuplicateBinOrderError(DefinitionError):
    def __init__(self, path: str, member_name: str) -> None:
        super().__init__(f"enum field '{path}' lists member '{member_name}' more than once in bin_order")


class MissingMaxLenError(DefinitionError):
    def __init__(self, path: str) -> None:
        super().__init__(f"list field '{path}' requires an explicit max_len= argument to bfield()")


class BitsNotApplicableToListError(DefinitionError):
    def __init__(self, path: str) -> None:
        super().__init__(
            f"field '{path}' is a list field and does not accept a bits= argument, "
            f"item width is derived from bin_order"
        )


class SignedNotApplicableError(DefinitionError):
    def __init__(self, path: str, annotation: object) -> None:
        super().__init__(f"field '{path}' of type {annotation!r} does not accept a signed= argument")


class MissingSignedError(DefinitionError):
    def __init__(self, path: str) -> None:
        super().__init__(f"int field '{path}' requires an explicit signed= argument to bfield()")


class NestedCallbackDataError(DefinitionError):
    def __init__(self, path: str) -> None:
        super().__init__(f"field '{path}' embeds a BinaryCallbackData subclass, use a plain BaseModel instead")


class CircularNestingError(DefinitionError):
    def __init__(self, path: str, model_name: str) -> None:
        super().__init__(f"field '{path}' introduces a circular reference back to model '{model_name}'")


class SizeLimitExceededError(DefinitionError):
    def __init__(self, total_bits: int, max_bits: int) -> None:
        super().__init__(f"schema needs {total_bits} bits, which exceeds the {max_bits} bit wire budget")


class PrefixCollisionError(DefinitionError):
    def __init__(self, prefix: int, existing_class_name: str, new_class_name: str) -> None:
        super().__init__(
            f"prefix {prefix} is already registered to '{existing_class_name}', "
            f"cannot register it again for '{new_class_name}'"
        )


class ExpectedTypeError(DefinitionError):
    def __init__(self, candidate: object) -> None:
        super().__init__(
            f"expected type {candidate!r} must be a subclass of BinaryCallbackData, "
            f"BinaryCallbackData itself is not allowed"
        )


class EncodeError(BinaryCallbackError):
    pass


class ValueOverflowError(EncodeError):
    def __init__(self, path: str, value: int, bits: int, signed: bool) -> None:
        signedness = "signed" if signed else "unsigned"
        super().__init__(f"value {value} for field '{path}' does not fit in {bits} {signedness} bits")


class ListLengthOverflowError(EncodeError):
    def __init__(self, path: str, length: int, max_len: int) -> None:
        super().__init__(f"list field '{path}' has {length} items, which exceeds max_len={max_len}")


class DecodeError(BinaryCallbackError):
    pass


class PrefixMismatchError(DecodeError):
    def __init__(self, actual_prefix: int, expected_prefix: Optional[int]) -> None:
        super().__init__(f"decoded prefix {actual_prefix} does not match expected prefix {expected_prefix}")


class VersionMismatchError(DecodeError):
    def __init__(self, actual_version: int, expected_version: int) -> None:
        super().__init__(f"decoded version {actual_version} does not match expected version {expected_version}")


class PrefixEnumMismatchError(BinaryCallbackError):
    def __init__(self, prefix: int, enum_cls: object) -> None:
        super().__init__(f"prefix {prefix} has no matching member in {enum_cls!r}")


class PayloadCorruptError(DecodeError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"payload is corrupt: {reason}")


class DecryptionError(DecodeError):
    def __init__(self, reason: str) -> None:
        super().__init__(f"payload could not be decrypted: {reason}")
