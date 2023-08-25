import pytest
import stim
import numpy as np
from dotg.utilities import CircuitUnderstander
from dotg.circuits import rotated_surface_code
from dotg.noise import DepolarizingNoise

toy_circuit = DepolarizingNoise(physical_error=1e-2).permute_circuit(
    rotated_surface_code(distance=2, rounds=1)
)

print(CircuitUnderstander(toy_circuit).parity_check)
print(CircuitUnderstander(toy_circuit).logical_check)
print(CircuitUnderstander(toy_circuit).error_probabilities)


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
            0.006651565037037021,
            0.021037052112592554,
            0.017120199560979963,
            0.0350030745182814,
            0.024922133333333308,
        ]
        assert error_probabilities == expected_error_probabilities
