"""This module provides access to the Belief-Propagation decoder from the LDPC package: 
https://github.com/quantumgizmos/ldpc"""
from typing import List, Tuple

import numpy as np
import stim
from ldpc import bp_decoder
from numpy.typing import NDArray
import warnings

from dotg.decoders.decoder_options import MessageUpdates
from dotg.utilities import CircuitUnderstander


class BeliefPropagation:
    """."""

    def __init__(
        self,
        circuit: stim.Circuit,
        max_iterations,
        message_updates: MessageUpdates | int = MessageUpdates.PROD_SUM,
    ) -> None:
        self.circuit = circuit
        self.max_iterations = max_iterations
        self.message_updates = message_updates
        if self.message_updates not in [0, 1]:
            raise ValueError(
                "Message update kwarg must be one of 0 (product-sum) or 1 (minimum sum)."
                f" Received: {self.message_updates}."
            )

        self._understander = CircuitUnderstander(circuit=circuit)

        self.parity_check = np.asarray(self._understander.parity_check)
        self.logical_check = np.asarray(self._understander.logical_check)
        self.error_probabilities = np.asarray(self._understander.error_probabilities)

        self._decoder = bp_decoder(
            parity_check_matrix=self.parity_check,
            max_iter=self.max_iterations,
            bp_method=self.message_updates,
            channel_probs=self.error_probabilities,
            input_vector_type=0,
        )

    def decode_syndrome(
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
        """
        syndrome = np.asarray(syndrome)

        error_pattern: NDArray = self._decoder.decode(np.asarray(syndrome))

        remaining_syndrome: NDArray = np.asarray(
            [
                sum(x * y for x, y in zip(parity_row, error_pattern))
                for parity_row in self.parity_check
            ]
            if self._decoder.converge
            else syndrome
        )

        return bool(self._decoder.converge), error_pattern, remaining_syndrome

    def logical_error(self, num_shots: int | float) -> float:
        warnings.warn(
            """As Belief Propagation is not guaranteed to converge on quantum codes, it 
            does not yet permit logical error functionality. This function will only 
            calculate the logical error on those cases where BP converges."""
        )


# if __name__ == "__main__":
#     from dotg.circuits import rotated_surface_code, color_code
#     from dotg.noise import DepolarizingNoise
#     from dotg.decoders._syndrome_sampler import Sampler

#     noisy_circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(
#         color_code(distance=5)
#     )
#     sampler = Sampler(circuit=noisy_circuit)
#     syndrome, logical = sampler(1, True)
#     bp = BeliefPropagation(circuit=noisy_circuit, max_iterations=5)

#     converged, err_pat, remaining = bp.decode_syndrome(syndrome=syndrome[0])

#     if converged:
#         assert all(x == 0 for x in (bp.parity_check @ err_pat - np.asarray(syndrome))[0])
#     else:
#         assert all(x == y for x, y in zip(syndrome[0], remaining))
