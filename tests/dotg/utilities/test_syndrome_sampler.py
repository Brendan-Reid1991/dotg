import pytest

from dotg.utilities import Sampler
from dotg.utilities._syndrome_sampler import (
    check_if_noisy_circuit,
    NoNoiseInCircuitError,
)

from tests.dotg.circuits import (
    NOISELESS_CIRCUIT,
    NOISY_CIRCUIT,
    MEASUREMENT_NOISE_ONLY_CIRCUIT,
)


@pytest.mark.parametrize(
    "circuit, output",
    [
        [NOISELESS_CIRCUIT, False],
        [NOISY_CIRCUIT, True],
        [MEASUREMENT_NOISE_ONLY_CIRCUIT, True],
    ],
)
def test_check_if_noisy_circuit(circuit, output):
    assert check_if_noisy_circuit(circuit=circuit) == output


class TestSampler:
    @pytest.fixture(scope="class")
    def sampler(self):
        return Sampler(NOISY_CIRCUIT)

    def test_error_raised_if_circuit_has_no_noise(self):
        sampler = Sampler(NOISELESS_CIRCUIT)
        with pytest.raises(NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]):
            sampler(NOISELESS_CIRCUIT)

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
