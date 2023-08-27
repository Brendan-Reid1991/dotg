from typing import Type

import pytest

from dotg.decoders._decoder_base_class import Decoder
from dotg.decoders._belief_propagation_base_class import LDPC_BeliefPropagationDecoder
from dotg.utilities._syndrome_sampler import NoNoiseInCircuitError, Sampler
from tests.unit.circuits import BasicCircuits


class BasicDecoderTests:
    DECODER_CLASS: Type[Decoder]

    def test_raises_NoNoiseError_for_no_noise(self, *args, **kwargs):
        with pytest.raises(NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]):
            self.DECODER_CLASS(
                BasicCircuits.GraphLike.NOISELESS_CIRCUIT, *args, **kwargs
            )
        with pytest.raises(NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]):
            self.DECODER_CLASS(
                BasicCircuits.HypergraphLike.NOISELESS_CIRCUIT, *args, **kwargs
            )


class BasicBeliefPropagationDecoderTests:
    DECODER_CLASS: Type[LDPC_BeliefPropagationDecoder]

    @pytest.fixture(scope="class")
    def decoder_graph(self):
        return self.DECODER_CLASS(
            circuit=BasicCircuits.GraphLike.NOISY_CIRCUIT,
            max_iterations=1,
            message_updates=0,
        )

    @pytest.fixture(scope="class")
    def decoder_hypergraph(self):
        return self.DECODER_CLASS(
            circuit=BasicCircuits.HypergraphLike.NOISY_CIRCUIT,
            max_iterations=1,
            message_updates=0,
        )

    @pytest.fixture(scope="class")
    def graph_syndrome(self):
        sampler = Sampler(BasicCircuits.GraphLike.NOISY_CIRCUIT)
        syn, _ = sampler(1, True)
        return syn[0]

    @pytest.fixture(scope="class")
    def hypergraph_syndrome(self):
        sampler = Sampler(BasicCircuits.HypergraphLike.NOISY_CIRCUIT)
        syn, _ = sampler(1, True)
        return syn[0]

    @pytest.fixture(scope="class")
    def decoder_graph(self):
        return self.DECODER_CLASS(
            circuit=BasicCircuits.GraphLike.NOISY_CIRCUIT,
            max_iterations=1,
            message_updates=0,
        )

    @pytest.mark.parametrize("iterations", [-1, 0])
    def test_invalid_max_iterations_raises_value_error(
        self,
        iterations,
    ):
        with pytest.raises(
            ValueError, match="Max iterations needs to be positive and non-zero."
        ):
            self.DECODER_CLASS(
                BasicCircuits.GraphLike.NOISY_CIRCUIT,
                max_iterations=iterations,
                message_updates=0,
            )

    @pytest.mark.parametrize("message_updates", [-1, 2])
    def test_invalid_message_updates_raises_value_error(self, message_updates):
        with pytest.raises(
            ValueError,
            match="Message update kwarg must be one of "
            r"0 \(product-sum\) or 1 \(minimum-sum\)",
        ):
            self.DECODER_CLASS(
                BasicCircuits.GraphLike.NOISY_CIRCUIT,
                max_iterations=1,
                message_updates=message_updates,
            )

    def test_num_iterations_is_0_before_decoding(self, decoder_graph):
        assert decoder_graph.num_iterations == 0

    def test_posterior_log_probability_odds_returns_all_0s_decoding_hasnt_happened(
        self, decoder_graph
    ):
        assert not any(decoder_graph.posterior_log_probability_odds)

    def test_posterior_probability_odds_returns_all_1s_decoding_hasnt_happened(
        self, decoder_graph
    ):
        assert all(decoder_graph.posterior_probability_odds)

    def test_posterior_probabilities_returns_all_pt5s_decoding_hasnt_happened(
        self, decoder_graph
    ):
        assert all(x == 0.5 for x in decoder_graph.posterior_probabilities)

    def test_posterior_probabilities_altered_after_decoding_and_most_are_unique_floats(
        self, decoder_graph, decoder_hypergraph, graph_syndrome, hypergraph_syndrome
    ):
        for decoder, syndrome in zip(
            [decoder_graph, decoder_hypergraph], [graph_syndrome, hypergraph_syndrome]
        ):
            decoder.decode_syndrome(syndrome)

            assert all(isinstance(x, float) for x in decoder.posterior_probabilities)
            assert (
                len(set(decoder.posterior_probabilities)) / len(decoder.parity_check[0])
                >= 0.9
            )

    def test_posterior_probability_odds_altered_after_decoding_and_most_are_unique_floats(
        self, decoder_graph, decoder_hypergraph, graph_syndrome, hypergraph_syndrome
    ):
        for decoder, syndrome in zip(
            [decoder_graph, decoder_hypergraph], [graph_syndrome, hypergraph_syndrome]
        ):
            decoder.decode_syndrome(syndrome)

            assert all(isinstance(x, float) for x in decoder.posterior_probability_odds)
            assert (
                len(set(decoder.posterior_probability_odds))
                / len(decoder.parity_check[0])
                >= 0.9
            )

    def test_posterior_log_probability_odds_altered_after_decoding_and_most_are_unique_floats(
        self, decoder_graph, decoder_hypergraph, graph_syndrome, hypergraph_syndrome
    ):
        for decoder, syndrome in zip(
            [decoder_graph, decoder_hypergraph], [graph_syndrome, hypergraph_syndrome]
        ):
            decoder.decode_syndrome(syndrome)

            assert all(
                isinstance(x, float) for x in decoder.posterior_log_probability_odds
            )
            assert (
                len(set(decoder.posterior_log_probability_odds))
                / len(decoder.parity_check[0])
                >= 0.9
            )
