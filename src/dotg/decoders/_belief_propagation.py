"""This module provides access to the Belief-Propagation decoder from the LDPC package: 
https://github.com/quantumgizmos/ldpc"""

import warnings
from typing import List, Tuple

import numpy as np
import stim
from numpy.typing import NDArray

from dotg.decoders._decoder_base_classes import (
    LDPCBeliefPropagationDecoder,
    LDPCDecoderOptions,
)
from dotg.utilities import Sampler


class BeliefPropagation(LDPCBeliefPropagationDecoder):
    """This class defines a Belief Propagation decoder (BP) from the LDPC package.


    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit that defines our experiment.
    decoder_options : LDPCDecoderOptions, optional
        Which decoder options to pass. The following options are available:
            - max_iterations: int
            - message_updats: MessageUpdates, optional
            - min_sum_scaling_factor: float, optional
        The options `osd_method` and `osd_order` have no affect on this class.
    """

    def __init__(
        self, circuit: stim.Circuit, decoder_options: LDPCDecoderOptions
    ) -> None:
        super().__init__(circuit=circuit, decoder_options=decoder_options)

        if self.decoder_options.osd_method is not None:
            self.decoder_options = LDPCDecoderOptions(
                max_iterations=decoder_options.max_iterations,
                message_updates=decoder_options.message_updates,
                min_sum_scaling_factor=decoder_options.min_sum_scaling_factor,
            )

    def decode_syndrome(  # type: ignore
        self, syndrome: List[int] | NDArray
    ) -> Tuple[bool, NDArray, NDArray]:
        """Decode a syndrome using belief propagation. As BP is not guaranteed to decode,
          this method returns a 3-tuple. The elements are as follows:
            - A boolean on whether or not the algorithm converged.
            - The final error pattern that the algorithm terminated on.
            - The remaining syndrome considering that error pattern. If the algorithm did
              not converge, this value is overwritten to be the input syndrome.

        Parameters
        ----------
        syndrome : List[int] | NDArray
            Array of syndromes.

        Returns
        -------
        Tuple[bool, NDArray, NDArray]
            Results from the algorithm. In order:
                - A boolean on whether or not the algorithm converged.
                - The final error pattern that the algorithm terminated on.
                - The remaining syndrome considering that error pattern. If the algorithm
                  did not converge, this value is overwritten to be the input syndrome.
            For more information see the docstring of decoders.LDPCDecoderOptions.
        """
        syndrome = np.asarray(syndrome)

        error_pattern: NDArray = self._decoder.decode(np.asarray(syndrome))

        remaining_syndrome: NDArray = (
            self.update_syndrome_from_error_pattern(
                syndrome=syndrome, error_pattern=error_pattern
            )
            if self._decoder.converge
            else syndrome
        )

        return bool(self._decoder.converge), error_pattern, remaining_syndrome

    def update_syndrome_from_error_pattern(
        self, syndrome: NDArray, error_pattern: NDArray
    ) -> NDArray:
        """Update the syndrome given an observed error pattern from the decoding
        algorithm. This is a mod2 sum of the syndrome and the product of the parity
        check matrix and the error pattern:

        Parameters
        ----------
        syndrome : NDArray
            The syndrome that was decoded.
        error_pattern : NDArray
            Error pattern found at the point of algorithm termination.

        Returns
        -------
        NDArray
            An updated syndrome array.
        """
        return np.asarray(
            [
                (sum(x * y for x, y in zip(parity_row, error_pattern)) + syndrome[idx])
                % 2
                for idx, parity_row in enumerate(self.parity_check)
            ]
        )

    def logical_error(  # type: ignore
        self, num_shots: int | float, exclude_empty: bool = False
    ) -> Tuple[float, float]:
        """Calculate the logical error probability of this decoder on the given circuit,
        over a number of syndromes.

        Parameters
        ----------
        num_shots : int | float
            Number of syndromes to sample.
        exclude_empty : bool
            Whether or not to exclude empty syndromes from the simulation, by default
            False.

        Raises
        ------
        warnings.warn
            As BP is not guaranteed to covnerge on quantum codes, it cannot provide a
            true logical error probability. As such, we report on only those cases where
            the algorithm converges.

        Returns
        -------
        Tuple[float, float]
            The logical error probability and the precision (1 over the sqrt of the
            number of samples).
        """
        warnings.warn(
            """As Belief Propagation is not guaranteed to converge on quantum codes, it 
            does not yet permit logical error functionality. This function will only 
            calculate the logical error on those cases where BP converges."""
        )

        sampler = Sampler(circuit=self.circuit)
        syndromes, logicals = sampler(num_shots=num_shots, exclude_empty=exclude_empty)

        logical_failures = 0
        convergence_events = 0
        for syndrome, logical in zip(syndromes, logicals):
            converged, error_pattern, _ = self.decode_syndrome(syndrome=syndrome)
            if not converged:
                continue

            convergence_events += 1
            logical_failures += self.is_logical_failure(error_pattern, logical)

        if convergence_events > 0:
            return logical_failures / convergence_events, 1 / np.sqrt(
                convergence_events
            )
        return 0, 0
