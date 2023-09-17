from typing import Type

import pytest
import stim

from dotg.circuits.quantum_memory._code_base_class import Code, CodeFamily


class BasicCodeFamilyTests:
    CODE_FAMILY = Type[CodeFamily]

    def test_passing_arguments_results_in_error(self):
        with pytest.raises(SyntaxError, match="Can't make use of the top level "):
            self.CODE_FAMILY(a=1, b=2)


class BasicCircuitTests:
    CODE: Type[Code]

    @pytest.mark.parametrize("distance", [3, 5, 7, 9])
    def test_return_type_is_always_stim_circuit(self, distance):
        assert isinstance(self.CODE(distance).circuit, stim.Circuit)

    def test_circuit_is_always_flattened(self):
        assert not any(
            isinstance(instruction, stim.CircuitRepeatBlock)
            for instruction in self.CODE(distance=5).circuit
        )

    def test_increasing_rounds_increases_length_of_circuit(self):
        code_5rounds = self.CODE(distance=3, rounds=5)
        code_3rounds = self.CODE(distance=3, rounds=3)
        assert len(code_5rounds.circuit) > len(code_3rounds.circuit)
