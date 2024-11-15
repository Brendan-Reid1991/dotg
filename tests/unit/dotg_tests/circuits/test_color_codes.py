from typing import Type

import pytest

from dotg.circuits import ColorCode
from dotg.circuits._code_base_class import Code
from tests.unit.dotg_tests.circuits._basic_circuit_tests import (
    BasicCircuitTests,
    BasicCodeFamilyTests,
)


class BasicColorSubCodeTests(BasicCircuitTests):
    CODE: Type[Code]

    @pytest.mark.parametrize("distance", [2, 4, 6, 8])
    def test_invalid_memory_basis_raises_error(self, distance):
        with pytest.raises(
            ValueError, match="Distance for the triangular color code must be odd."
        ):
            self.CODE(distance=distance)


class TestColorCode(BasicCodeFamilyTests):
    CODE_FAMILY = ColorCode

    class TestTriangular(BasicColorSubCodeTests):
        CODE = ColorCode.Triangular
