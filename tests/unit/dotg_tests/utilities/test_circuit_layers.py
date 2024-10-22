import pytest
import stim

from dotg.utilities import get_circuit_layers


class TestGetCircuitLayers:
    @pytest.fixture(scope="class")
    def simple_circuit(self):
        return stim.Circuit(
            """
            R 0 1 2
            TICK
            M 0 1 2
            """
        )

    def test_basic_functionality(self, simple_circuit):
        subcircuits = get_circuit_layers(simple_circuit)
        assert (
            len(subcircuits) == 2
        ), "Fixture `simple_circuit` should result in two subcircuits."
        assert all(
            isinstance(x, stim.Circuit) for x in subcircuits
        ), "Each element should be of type stim.Circuit."
        assert isinstance(
            subcircuits, list
        ), "Output from get_circuit_layers is expected to be a list."
