"""This module provides access to the BPOSD decoder from the ldpc package: 
https://github.com/quantumgizmos/ldpc"""

import stim
from ldpc import bposd_decoder

from dotg.decoders._belief_propagation_base_class import (
    LDPCBeliefPropagationDecoder,
    LDPCDecoderOptions,
    MessageUpdates,
    OSDMethods,
)


class BPOSD(LDPCBeliefPropagationDecoder):
    """Unfinished."""

    def __init__(
        self, circuit: stim.Circuit, decoder_options: LDPCDecoderOptions
    ) -> None:
        super().__init__(circuit=circuit, decoder_options=decoder_options)
        if not decoder_options.osd_method:
            raise ValueError("You must provide an OSD method to use BPOSD.")

        raise NotImplementedError("Haven't gotten around to this one yet.")
