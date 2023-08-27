import pytest

from dotg.decoders import BeliefPropagation
from dotg.decoders._belief_propagation_base_class import MessageUpdates
from tests.unit.circuits._basic_circuits import BasicCircuits
from tests.unit.decoders._basic_decoder_tests import (
    BasicDecoderTests,
    BasicBeliefPropagationDecoderTests,
)
from dotg.utilities import Sampler

if __name__ == "__main__":
    circ = BasicCircuits.GraphLike.NOISY_CIRCUIT

    sampler = Sampler(circ)
    syndromes, logicals = sampler(1, True)


def test_message_updates_int_enum():
    assert [x.name for x in MessageUpdates] == ["PROD_SUM", "MIN_SUM"]
    assert [x.value for x in MessageUpdates] == [0, 1]


MAX_ITERATIONS = 1
MESSAGE_UPDATES = MessageUpdates.PROD_SUM


class TestBeliefPropagation(BasicBeliefPropagationDecoderTests, BasicDecoderTests):
    DECODER_CLASS = BeliefPropagation

    def test_raises_NoNoiseError_for_no_noise(self):
        return super().test_raises_NoNoiseError_for_no_noise(
            max_iterations=1, message_updates=0
        )

    def test_return_types_from_decode_syndrome(self, decoder_graph):
        pass

    def test_not_converging_results_in_same_syndrome_being_returned(self, decoder_graph):
        syndrome = [0, 1]
        converged, _, remaining_syndrome = decoder_graph.decode_syndrome(syndrome)
        assert not converged
        assert (remaining_syndrome == syndrome).all()

    def test_convergence_results_in_zero_syndrome_being_returned(self, decoder_graph):
        syndrome = [1, 1]
        converged, _, remaining = decoder_graph.decode_syndrome(syndrome)
        assert converged
        assert not all(remaining)

    def test_convergence_property(self, decoder_graph):
        syndrome = [1, 1]
        decoder_graph.decode_syndrome(syndrome)
        assert decoder_graph.converged
