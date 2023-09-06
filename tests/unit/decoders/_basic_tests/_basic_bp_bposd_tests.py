from typing import Type
import pytest
from dotg.decoders._belief_propagation_base_class import (
    LDPC_BeliefPropagationDecoder,
    LDPC_DecoderOptions,
)
from dotg.utilities import Sampler
from tests.unit.circuits import BasicCircuits


class BasicBeliefPropagationDecoderTests:
    DECODER_CLASS: Type[LDPC_BeliefPropagationDecoder]

    @pytest.fixture(scope="class")
    def decoder_graph(self):
        return self.DECODER_CLASS(
            circuit=BasicCircuits.GraphLike.NOISY_CIRCUIT,
            decoder_options=LDPC_DecoderOptions(max_iterations=1, message_updates=0),
        )

    @pytest.fixture(scope="class")
    def decoder_hypergraph(self):
        return self.DECODER_CLASS(
            circuit=BasicCircuits.HypergraphLike.NOISY_CIRCUIT,
            decoder_options=LDPC_DecoderOptions(max_iterations=1, message_updates=0),
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
            decoder_options=LDPC_DecoderOptions(max_iterations=1, message_updates=0),
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
