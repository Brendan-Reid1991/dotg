from typing import List, Type

import numpy as np
import pytest
from numpy.typing import NDArray

from dotg.decoders import MinimumWeightPerfectMatching
from tests.unit.circuits import BasicCircuits
from tests.unit.decoders._basic_decoder_tests import BasicDecoderTests


class TestMinimumWeightPerfectMatching(BasicDecoderTests):
    DECODER_CLASS = MinimumWeightPerfectMatching

    @pytest.fixture(scope="class")
    def mwpm(self):
        return MinimumWeightPerfectMatching(BasicCircuits.GraphLike.NOISY_CIRCUIT)

    def test_non_graph_like_circuit_raises_error(self):
        with pytest.raises(
            ValueError,
            match="Circuit passed does not permit a graph-like error model, ",
        ):
            MinimumWeightPerfectMatching(BasicCircuits.HypergraphLike.NOISY_CIRCUIT)

    def test_decode_syndrome(self, mwpm):
        syndrome = mwpm.sampler.sample(shots=1)
        assert isinstance(mwpm.decode_syndrome(syndrome=syndrome[0]), np.ndarray)

    def test_logical_error_returns_float(self, mwpm):
        assert isinstance(mwpm.logical_error(num_shots=1000), float)
