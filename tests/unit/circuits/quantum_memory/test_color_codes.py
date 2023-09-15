import pytest
from typing import Type

from dotg.circuits.quantum_memory import ColorCode
from dotg.circuits.quantum_memory._code_base_class import _Code
from tests.unit.circuits._basic_circuit_tests import (
    BasicCodeFamilyTests,
    BasicCircuitTests,
)


class BasicColorSubCodeTests(BasicCircuitTests):
    CODE: Type[_Code]

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
