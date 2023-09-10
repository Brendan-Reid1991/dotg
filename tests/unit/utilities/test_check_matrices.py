import numpy as np
import pytest
import stim

from dotg.circuits.quantum_memory import rotated_surface_code
from dotg.noise import DepolarizingNoise
from dotg.utilities import CircuitUnderstander

toy_circuit = DepolarizingNoise(physical_error=1e-2).permute_circuit(
    rotated_surface_code(distance=2, rounds=1)
)


class TestCircuitUnderstander:
    @pytest.fixture(scope="class")
    def circuit_understander(self):
        return CircuitUnderstander(toy_circuit)

    @pytest.fixture(scope="class")
    def parity_check(self, circuit_understander):
        return circuit_understander.parity_check

    @pytest.fixture(scope="class")
    def logical_check(self, circuit_understander):
        return circuit_understander.logical_check

    @pytest.fixture(scope="class")
    def error_probabilities(self, circuit_understander):
        return circuit_understander.error_probabilities

    def test_parity_check_is_as_expected(self, parity_check):
        expected_parity_check = np.asarray([[1, 1, 1, 0, 0], [0, 1, 0, 1, 1]])
        assert (parity_check == expected_parity_check).all()

    def test_logical_check_is_as_expected(self, logical_check):
        expected_logical_check = np.asarray([0, 0, 1, 0, 1])
        assert (logical_check == expected_logical_check).all()

    def test_error_probabilities_are_as_expected(self, error_probabilities):
        expected_error_probabilities = [
            0.00927749898298139,
            0.022313435150607193,
            0.019690412355673134,
            0.03871067202638849,
            0.028710110023255343,
        ]
        assert error_probabilities == expected_error_probabilities
