import pytest

from dotg.decoders import BPOSD
from dotg.decoders._belief_propagation_base_class import (
    LDPCDecoderOptions,
    MessageUpdates,
    OSDMethods,
)
from tests.unit.dotg_tests.decoders._basic_tests._basic_bp_bposd_tests import (
    BasicBeliefPropagationDecoderTests,
    BasicMemoryCircuits,
)
from tests.unit.dotg_tests.decoders._basic_tests._basic_decoder_tests import (
    BasicDecoderTests,
)


class TestBPOSD(BasicBeliefPropagationDecoderTests, BasicDecoderTests):
    DECODER_CLASS = BPOSD

    def test_error_raised_if_no_osd_method_passed(self):
        with pytest.raises(
            ValueError, match="You must provide an OSD method to use BPOSD."
        ):
            BPOSD(
                circuit=BasicMemoryCircuits.GraphLike.NOISY_CIRCUIT,
                decoder_options=LDPCDecoderOptions(max_iterations=20),
            )

    @pytest.fixture(scope="class")
    def options(self):
        return LDPCDecoderOptions(
            max_iterations=2, osd_method=OSDMethods.EXHAUSTIVE, osd_order=2
        )

    @pytest.fixture(scope="class")
    def decoder_graph(self, options):
        return self.DECODER_CLASS(
            circuit=BasicMemoryCircuits.GraphLike.NOISY_CIRCUIT,
            decoder_options=options,
        )

    @pytest.fixture(scope="class")
    def decoder_hypergraph(self, options):
        return self.DECODER_CLASS(
            circuit=BasicMemoryCircuits.HypergraphLike.NOISY_CIRCUIT,
            decoder_options=options,
        )

    def test_raises_NoNoiseError_for_no_noise(self, options):
        return super().test_raises_NoNoiseError_for_no_noise(options)

    # TODO Rewrite this test!!
    def test_logical_error(self, decoder_hypergraph):
        decoder_hypergraph.logical_error(10)
