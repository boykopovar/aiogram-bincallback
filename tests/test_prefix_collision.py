import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import NestedCallbackDataError
from aiogram_bincallback import PrefixCollisionError
from aiogram_bincallback import PrefixMismatchError
from aiogram_bincallback import VersionMismatchError
from aiogram_bincallback import bfield


def test_registering_two_classes_with_same_prefix_raises_prefix_collision_error():
    class FirstCb(BinaryCallbackData, prefix=9001, version=1):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises(PrefixCollisionError) as excinfo:
        class SecondCb(BinaryCallbackData, prefix=9001, version=1):
            other: int = bfield(bits=8, signed=False)

    assert "9001" in str(excinfo.value)


def test_same_prefix_different_version_does_not_collide_but_same_prefix_same_version_does():
    class BaseVersionCb(BinaryCallbackData, prefix=9002, version=1):
        value: int = bfield(bits=8, signed=False)

    class OtherVersionCb(BinaryCallbackData, prefix=9002, version=2):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises(PrefixCollisionError):
        class CollidingCb(BinaryCallbackData, prefix=9002, version=1):
            other: int = bfield(bits=8, signed=False)


def test_registering_two_classes_with_different_prefixes_does_not_raise():
    class FirstUniqueCb(BinaryCallbackData, prefix=9101, version=1):
        value: int = bfield(bits=8, signed=False)

    class SecondUniqueCb(BinaryCallbackData, prefix=9102, version=1):
        value: int = bfield(bits=8, signed=False)

    assert FirstUniqueCb.__bin_prefix__ == 9101
    assert SecondUniqueCb.__bin_prefix__ == 9102


def test_registering_three_versions_of_same_prefix_does_not_raise():
    class VersionOneOfThreeCb(BinaryCallbackData, prefix=9103, version=1):
        value: int = bfield(bits=8, signed=False)

    class VersionTwoOfThreeCb(BinaryCallbackData, prefix=9103, version=2):
        value: int = bfield(bits=8, signed=False)

    class VersionThreeOfThreeCb(BinaryCallbackData, prefix=9103, version=3):
        value: int = bfield(bits=8, signed=False)

    assert VersionOneOfThreeCb.__bin_version__ == 1
    assert VersionTwoOfThreeCb.__bin_version__ == 2
    assert VersionThreeOfThreeCb.__bin_version__ == 3


def test_nesting_binary_callback_data_inside_another_raises_nested_callback_data_error():
    class InnerCb(BinaryCallbackData, prefix=9201, version=1):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises(NestedCallbackDataError):
        class OuterCb(BinaryCallbackData, prefix=9202, version=1):
            inner: InnerCb


def test_unpack_with_mismatched_prefix_raises_prefix_mismatch_error():
    class PrefixOneCb(BinaryCallbackData, prefix=9301, version=1):
        value: int = bfield(bits=8, signed=False)

    class PrefixTwoCb(BinaryCallbackData, prefix=9302, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = PrefixOneCb(value=5).pack()

    with pytest.raises(PrefixMismatchError):
        PrefixTwoCb.unpack(packed)


def test_unpack_with_mismatched_version_raises_version_mismatch_error():
    class VersionOneCb(BinaryCallbackData, prefix=9401, version=1):
        value: int = bfield(bits=8, signed=False)

    packed = VersionOneCb(value=5).pack()

    class VersionTwoCb(BinaryCallbackData, prefix=9401, version=2):
        value: int = bfield(bits=8, signed=False)

    with pytest.raises(VersionMismatchError):
        VersionTwoCb.unpack(packed)
