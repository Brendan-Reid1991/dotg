"""This module provides access to the BPOSD decoder from the ldpc package: 
https://github.com/quantumgizmos/ldpc"""

from typing import List

import numpy as np
import stim
from numpy.typing import NDArray

from dotg.decoders._belief_propagation_base_class import (
    LDPCBeliefPropagationDecoder,
    LDPCDecoderOptions,
)
from dotg.utilities import Sampler


class BPOSD(LDPCBeliefPropagationDecoder):
    """The BPOSD decoder. A two stage decoder that decodes with belief propagation and,
    upon failure to converge, passes the posterior error probability distribution to an
    Order Statistics Decoder for a solution. The OSD step can become very slow for high
    distances.

    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit that defines our experiment.
    decoder_options : LDPCDecoderOptions, optional
        Which decoder options to pass. The following options are available:
            - max_iterations: int
            - message_updats: MessageUpdates, optional
            - min_sum_scaling_factor: float, optional
            - osd_method: OSDMethods
            - osd_order: int, optional
        For more information see the docstring of decoders.LDPCDecoderOptions.
    """

    def __init__(
        self, circuit: stim.Circuit, decoder_options: LDPCDecoderOptions
    ) -> None:
        super().__init__(circuit=circuit, decoder_options=decoder_options)
        if not decoder_options.osd_method:
            raise ValueError("You must provide an OSD method to use BPOSD.")

    def decode_syndrome(self, syndrome: List[int] | NDArray) -> NDArray:
        return self._decoder.decode(np.asarray(syndrome))

    def logical_error(
        self, num_shots: int | float, exclude_empty: bool = False
    ) -> float:
        sampler = Sampler(circuit=self.circuit)
        syndromes, logicals = sampler(num_shots=num_shots, exclude_empty=exclude_empty)

        logical_failures = 0
        for syndrome, logical in zip(syndromes, logicals):
            error_pattern = self.decode_syndrome(syndrome=syndrome)
            logical_failures += self.is_logical_failure(error_pattern, logical)

        return logical_failures / num_shots
