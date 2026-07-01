from typing import Optional
from typing import Sequence
from typing import Tuple


class BinaryCallbackError(ValueError):
    pass


class DefinitionError(BinaryCallbackError):
    pass


class UnsupportedFieldTypeError(DefinitionError):
    def __init__(self, path: str, annotation: object) -> None:
        ...


class MissingBitsError(DefinitionError):
    def __init__(self, path: str) -> None:
        ...


class MissingBinOrderError(DefinitionError):
    def __init__(self, path: str) -> None:
        ...


class InsufficientBitsError(DefinitionError):
    def __init__(self, path: str, bits: int, required_bits: int) -> None:
        ...


class SignedNotApplicableError(DefinitionError):
    def __init__(self, path: str, annotation: object) -> None:
        ...


class MissingSignedError(DefinitionError):
    def __init__(self, path: str) -> None:
        ...


class NestedOptionalError(DefinitionError):
    def __init__(self, path: str) -> None:
        ...


class NestedCallbackDataError(DefinitionError):
    def __init__(self, path: str) -> None:
        ...


class CircularNestingError(DefinitionError):
    def __init__(self, path: str, model_name: str) -> None:
        ...


class SizeLimitExceededError(DefinitionError):
    def __init__(self, total_bits: int, max_bits: int) -> None:
        ...


class PrefixCollisionError(DefinitionError):
    def __init__(self, prefix: int, existing_class_name: str, new_class_name: str) -> None:
        ...


class EncodeError(BinaryCallbackError):
    pass


class ValueOverflowError(EncodeError):
    def __init__(self, path: str, value: int, bits: int, signed: bool) -> None:
        ...


class DecodeError(BinaryCallbackError):
    pass


class PrefixMismatchError(DecodeError):
    def __init__(self, actual_prefix: int, expected_prefix: int) -> None:
        ...


class VersionMismatchError(DecodeError):
    def __init__(self, actual_version: int, expected_version: int) -> None:
        ...


class PayloadCorruptError(DecodeError):
    def __init__(self, reason: str) -> None:
        ...
