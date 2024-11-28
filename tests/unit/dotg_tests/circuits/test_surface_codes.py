from typing import Type

import pytest

from dotg.circuits import SurfaceCode
from dotg.circuits._surface_codes import SurfaceCodeSubClass
from tests.unit.dotg_tests.circuits._basic_circuit_tests import (
    BasicCircuitTests,
    BasicCodeFamilyTests,
)


class BasicSurfaceSubCodeTests(BasicCircuitTests):
    CODE: Type[SurfaceCodeSubClass]

    def test_invalid_memory_basis_raises_error(self):
        with pytest.raises(ValueError, match="Memory basis must be one of `X` or `Z`."):
            self.CODE(distance=3, memory_basis="t")


class TestSurfaceCode(BasicCodeFamilyTests):
    CODE_FAMILY = SurfaceCode

    class TestRotated(BasicSurfaceSubCodeTests):
        CODE = SurfaceCode.Rotated

    class TestUnrotated(BasicSurfaceSubCodeTests):
        CODE = SurfaceCode.Unrotated
