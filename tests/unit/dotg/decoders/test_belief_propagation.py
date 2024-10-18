from typing import Type

import ldpc.bp_decoder as ldpc_bp
import numpy as np
import pytest

from dotg.decoders import BeliefPropagation
from dotg.decoders._belief_propagation_base_class import (
    LDPCDecoderOptions,
    MessageUpdates,
)
from tests.unit.decoders._basic_tests._basic_bp_bposd_tests import (
    BasicBeliefPropagationDecoderTests,
    BasicMemoryCircuits,
)
from tests.unit.decoders._basic_tests._basic_decoder_tests import BasicDecoderTests

# TODO: Improve these tests; Coverage is 94% but tests are not very robust.


class TestBeliefPropagation(BasicBeliefPropagationDecoderTests, BasicDecoderTests):
    DECODER_CLASS = BeliefPropagation

    def test_raises_NoNoiseError_for_no_noise(self, *args, **kwargs):
        return super().test_raises_NoNoiseError_for_no_noise(
            LDPCDecoderOptions(max_iterations=1, message_updates=MessageUpdates.PROD_SUM)
        )

    @pytest.mark.parametrize(
        "decoder_options, expected_max_iterations, expected_message_updates_str, expected_min_sum_scaling_factor",
        [
            [
                LDPCDecoderOptions(max_iterations=25, message_updates=0),
                25,
                "product_sum",
                1,
            ],
            [
                LDPCDecoderOptions(max_iterations=13, message_updates=1),
                13,
                "minimum_sum_log",
                1,
            ],
            [
                LDPCDecoderOptions(
                    max_iterations=40, message_updates=1, min_sum_scaling_factor=15
                ),
                40,
                "minimum_sum_log",
                15,
            ],
        ],
    )
    def test_return_type_and_settings_from_decoder_property(
        self,
        decoder_options,
        expected_max_iterations,
        expected_message_updates_str,
        expected_min_sum_scaling_factor,
    ):
        bp_decoder = BeliefPropagation(
            circuit=BasicMemoryCircuits.GraphLike.NOISY_CIRCUIT,
            decoder_options=decoder_options,
        )
        decoder = bp_decoder.decoder
        assert isinstance(
            decoder, ldpc_bp
        ), f"Decoder was of type {type(decoder)}; should have been {type(ldpc_bp)}."
        assert (
            decoder.max_iter == expected_max_iterations
        ), f"Decoder max iterations was {decoder.max_iter}; should have been {expected_max_iterations}."
        assert (
            decoder.bp_method == expected_message_updates_str
        ), f"Decoder bp_method was {decoder.bp_method}; should have been {expected_message_updates_str}."
        assert (
            decoder.ms_scaling_factor == expected_min_sum_scaling_factor
        ), f"Min sum scaling factor was {decoder.ms_scaling_factor}; should have been {expected_min_sum_scaling_factor}"

    @pytest.mark.parametrize("osd_method, osd_order", [(0, 10), (1, 11), (2, 3)])
    def test_setting_osd_options_has_no_effect(self, osd_method, osd_order):
        bp_decoder = BeliefPropagation(
            circuit=BasicMemoryCircuits.HypergraphLike.NOISY_CIRCUIT,
            decoder_options=LDPCDecoderOptions(
                max_iterations=30,
                message_updates=MessageUpdates.MIN_SUM,
                osd_method=osd_method,
                osd_order=osd_order,
            ),
        )

        assert (
            bp_decoder.decoder_options.osd_method is None
        ), "OSD method parameter of decoder_options was not properly erased."
        assert (
            bp_decoder.decoder_options.osd_order is None
        ), "OSD order parameter of decoder_options was not properly erased."

    def test_return_types_from_decode_syndrome(self, decoder_graph):
        syndrome = [0, 1]
        converged, error_pattern, remaining_syndrome = decoder_graph.decode_syndrome(
            syndrome
        )

        def _error_message(place: str, true_type: Type, received: Type):
            return f"{place} return type of BeliefPropagation.decode_syndrome should be {true_type}. Received: {received}"

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
            decoder_graph.logical_error(10)
        with pytest.warns(match=match):
            decoder_hypergraph.logical_error(10)
