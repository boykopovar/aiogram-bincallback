import pytest
from pydantic import BaseModel

from aiogram_bincallback.core import CircularNestingError
from aiogram_bincallback.planning import build_codec_plan


def test_direct_self_reference_raises_circular_nesting_error():
    class Node(BaseModel):
        child: "Node"

    Node.model_fields["child"].annotation = Node

    with pytest.raises(CircularNestingError) as excinfo:
        build_codec_plan(Node)

    assert "Node" in str(excinfo.value)


def test_indirect_two_hop_reference_raises_circular_nesting_error():
    class A(BaseModel):
        b: "B"

    class B(BaseModel):
        a: A

    A.model_fields["b"].annotation = B

    with pytest.raises(CircularNestingError) as excinfo:
        build_codec_plan(A)

    assert "A" in str(excinfo.value)
