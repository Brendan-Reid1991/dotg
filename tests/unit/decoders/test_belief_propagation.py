from typing import Type
import pytest
import numpy as np

from dotg.decoders import BeliefPropagation
from dotg.decoders._belief_propagation_base_class import MessageUpdates
from tests.unit.decoders._basic_decoder_tests import (
    BasicDecoderTests,
    BasicBeliefPropagationDecoderTests,
)


# TODO: Improve these tests; Coverage is 96% but tests are not very robust.


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
        syndrome = [0, 1]
        converged, error_pattern, remaining_syndrome = decoder_graph.decode_syndrome(
            syndrome
        )

        def _error_message(place: str, true_type: Type, received: Type):
            return f"{place} return type of BeliefPropagatino.decode_syndrome should be {true_type}. Received: {received}"

        assert isinstance(converged, bool), _error_message(
            "First", bool, type(converged)
        )

        assert isinstance(error_pattern, np.ndarray), _error_message(
            "Second", np.ndarray, type(error_pattern)
        )

        assert isinstance(remaining_syndrome, np.ndarray), _error_message(
            "Third", np.ndarray, type(remaining_syndrome)
        )

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

    @pytest.mark.parametrize(
        "syndrome, error_pattern, expected",
        [([0, 0], [1, 1], [0, 1]), ([0, 1], [0, 0], [0, 1]), ([1, 1], [0, 0], [1, 1])],
    )
    def test_update_syndrome_from_error_pattern(
        self, decoder_graph, syndrome, error_pattern, expected
    ):
        """If this test fails, double check the `expected` entry by calling
        [
          (sum(x * y) for x, y in zip(pcm, error_pattern) + syndyome[idx]) % 2
              for idx, pcm in enumerate(parity_check_matrix)
        ]
        where parity_check_matrix = dotg.utilites.CircuitUnderstander(decoder_graph.circuit).parity_check
        """
        assert (
            decoder_graph.update_syndrome_from_error_pattern(syndrome, error_pattern)
            == expected
        ).all()

    def test_logical_error_raises_warning(self, decoder_graph, decoder_hypergraph):
        match = """As Belief Propagation is not guaranteed to converge on quantum codes, it 
            does not yet permit logical error functionality. This function will only 
            calculate the logical error on those cases where BP converges."""
        with pytest.warns(match=match):
            decoder_graph.logical_error(1)
        with pytest.warns(match=match):
            decoder_hypergraph.logical_error(1)
