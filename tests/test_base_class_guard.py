from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import bfield


def test_binary_callback_data_base_class_has_no_bin_plan():
    assert "__bin_plan__" not in BinaryCallbackData.__dict__


def test_pydantic_init_subclass_hook_returns_early_for_base_class_itself():
    BinaryCallbackData.__pydantic_init_subclass__()

    assert "__bin_plan__" not in BinaryCallbackData.__dict__


def test_binary_callback_data_base_class_has_default_prefix_and_version():
    assert BinaryCallbackData.__bin_prefix__ is None
    assert BinaryCallbackData.__bin_version__ == 1


def test_subclass_without_prefix_does_not_register_but_still_builds_plan():
    class UnregisteredCb(BinaryCallbackData):
        value: int = bfield(bits=8, signed=False)

    assert UnregisteredCb.__bin_prefix__ is None
    assert len(UnregisteredCb.__bin_plan__) == 1


def test_subclassing_twice_builds_independent_plans_for_each_level():
    class LevelOneCb(BinaryCallbackData, prefix=9601, version=1):
        value: int = bfield(bits=8, signed=False)

    class LevelTwoCb(BinaryCallbackData, prefix=9602, version=1):
        other: int = bfield(bits=4, signed=False)

    assert [codec.name for codec in LevelOneCb.__bin_plan__] == ["value"]
    assert [codec.name for codec in LevelTwoCb.__bin_plan__] == ["other"]
