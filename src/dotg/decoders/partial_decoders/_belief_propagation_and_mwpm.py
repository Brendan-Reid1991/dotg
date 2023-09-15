import stim

from dotg.decoders import BeliefPropagation, MinimumWeightPerfectMatching
from dotg.decoders._belief_propagation_base_class import (
    LDPC_DecoderOptions,
    MessageUpdates,
)
from dotg.decoders._decoder_base_class import Decoder


class BP_MWPM(Decoder):
    pass

    def __init__(
        self,
        circuit: stim.Circuit,
        decoder_options: LDPC_DecoderOptions = LDPC_DecoderOptions(
            max_iterations=10, message_updates=MessageUpdates.PROD_SUM
        ),
    ) -> None:
        super().__init__(circuit=circuit)
