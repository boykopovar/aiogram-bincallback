import pytest

from aiogram_bincallback import BinaryCallbackData
from aiogram_bincallback import SizeLimitExceededError
from aiogram_bincallback import bfield
from aiogram_bincallback.wire import MAX_PAYLOAD_BITS


def test_defining_class_within_payload_budget_does_not_raise():
    class WithinBudgetCb(BinaryCallbackData, prefix=3001, version=1):
        value: int = bfield(bits=8, signed=False)

    assert WithinBudgetCb.__bin_prefix__ == 3001


def test_defining_class_exceeding_payload_budget_raises_size_limit_exceeded_error():
    with pytest.raises(SizeLimitExceededError) as excinfo:
        class TooLargeCb(BinaryCallbackData, prefix=3002, version=1):
            value: int = bfield(bits=MAX_PAYLOAD_BITS + 1, signed=False)

    assert str(MAX_PAYLOAD_BITS) in str(excinfo.value)


def test_defining_class_exactly_at_payload_budget_does_not_raise():
    class ExactBudgetCb(BinaryCallbackData, prefix=3003, version=1):
        value: int = bfield(bits=MAX_PAYLOAD_BITS, signed=False)

    assert ExactBudgetCb.__bin_prefix__ == 3003


def test_size_limit_accounts_for_nested_basemodel_fields_recursively():
    from pydantic import BaseModel

    class Inner(BaseModel):
        value: int = bfield(bits=MAX_PAYLOAD_BITS - 4, signed=False)

    with pytest.raises(SizeLimitExceededError):
        class NestedTooLargeCb(BinaryCallbackData, prefix=3004, version=1):
            extra: int = bfield(bits=8, signed=False)
            inner: Inner
