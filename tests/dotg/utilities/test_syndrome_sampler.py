import pytest
import stim

from dotg.circuits import rotated_surface_code
from dotg.noise import DepolarizingNoise, NoiseModel
from dotg.utilities import Sampler
from dotg.utilities.stim_assets import MeasurementGates
from dotg.utilities._syndrome_sampler import (
    check_if_noisy_circuit,
    NoNoiseInCircuitError,
)

noiseless_circuit = rotated_surface_code(distance=2, rounds=1)
generic_noise_model = DepolarizingNoise(physical_error=1e-2)
noisy_circuit = generic_noise_model.permute_circuit(noiseless_circuit)

measurement_noise_only = NoiseModel(measurement_noise=1e-2)
noisy_circuit_only_measurement_errors = measurement_noise_only.permute_circuit(
    noiseless_circuit
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


class TestSampler:
    @pytest.fixture(scope="class")
    def sampler(self):
        return Sampler(noisy_circuit)

    def test_error_raised_if_circuit_has_no_noise(self):
        sampler = Sampler(noiseless_circuit)
        with pytest.raises(NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]):
            sampler(noiseless_circuit)

    @pytest.mark.parametrize("exclude_empty", [True, False])
    @pytest.mark.parametrize("num_shots", [59, 723, 1467])
    def test_return_array_length_is_consistent_regardless_of_empty_exclusion(
        self, sampler, exclude_empty, num_shots
    ):
        syndrome_batch, logical_batch = sampler(num_shots, exclude_empty)

        assert len(syndrome_batch) == num_shots
        assert len(logical_batch) == num_shots

    @pytest.mark.parametrize("repeat", [50])
    def test_no_empty_syndromes_if_exclude_empty(self, sampler, repeat):
        for _ in range(repeat):
            syndrome_batch, _ = sampler(100, True)
            assert all(any(syn) for syn in syndrome_batch)

    @pytest.mark.parametrize("repeat", [50])
    def test_some_empty_syndromes_if_not_exclude_empty(self, sampler, repeat):
        # Randomised test! Likelihood of failing is neglible, but still.

        for _ in range(repeat):
            syndrome_batch, _ = sampler(100, False)
            assert any(not any(syn) for syn in syndrome_batch)
