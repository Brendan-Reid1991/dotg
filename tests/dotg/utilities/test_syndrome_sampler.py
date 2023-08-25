import pytest
import stim

from dotg.utilities import Sampler
from dotg.utilities.stim_assets import MeasurementGates
from dotg.utilities._syndrome_sampler import (
    check_if_noisy_circuit,
    NoNoiseInCircuitError,
)

noiseless_circuit = stim.Circuit(
    """R 0
    H 0 
    M 0"""
)

noisy_circuit = stim.Circuit(
    """R 0
    DEPOLARIZE1(0.01) 0
    H 0
    X_ERROR(.011) 9
    M(.1) 0
    """
)

noisy_circuit_only_measurement_errors = stim.Circuit(
    """R 0
    H 0
    M(.1) 0
    """
)


@pytest.mark.parametrize(
    "circuit, output",
    [
        [noiseless_circuit, False],
        [noisy_circuit, True],
        [noisy_circuit_only_measurement_errors, True],
    ],
)
def test_check_if_noisy_circuit(circuit, output):
    assert check_if_noisy_circuit(circuit=circuit) == output
