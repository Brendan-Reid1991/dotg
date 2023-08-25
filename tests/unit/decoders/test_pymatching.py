import pytest
from dotg.decoders import MinimumWeightPerfectMatching
from tests.unit.circuits import NOISY_CIRCUIT


class TestMinimumWeightPerfectMatching:
    @pytest.fixture(scope="class")
    def mwpm(self):
        return MinimumWeightPerfectMatching
