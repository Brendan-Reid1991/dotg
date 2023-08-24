"""This module provides access to the Belief-Propagation decoder from the LDPC package: 
https://github.com/quantumgizmos/ldpc"""
import warnings
from enum import IntEnum
from typing import List, Tuple

import numpy as np
import stim
from ldpc import bp_decoder
from numpy.typing import NDArray

from dotg.decoders import Sampler
from dotg.decoders._decoder_base_class import Decoder
from dotg.utilities import CircuitUnderstander


class MessageUpdates(IntEnum):
    """An enum for accessing min-sum and prod-sum updates in belief propagation.

    Options:
        - PROD_SUM = 0
        - MIN_SUM = 1
    """

    PROD_SUM: int = 0
    MIN_SUM: int = 1


class BeliefPropagation(Decoder):
    """."""

    def __init__(
        self,
        circuit: stim.Circuit,
        max_iterations,
        message_updates: MessageUpdates | int = MessageUpdates.PROD_SUM,
    ) -> None:
        super().__init__(circuit=circuit)
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
                sum(x * y for x, y in zip(parity_row, error_pattern)) % 2
                for parity_row in self.parity_check
            ]
            if self._decoder.converge
            else syndrome
        )

        return bool(self._decoder.converge), error_pattern, remaining_syndrome

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
            _logical_flip_observed = [
                sum(x * y for x, y in zip(log, error_pattern)) % 2
                for log in self.logical_check
            ]

            if _logical_flip_observed != logical:
                logical_failures += 1

        return logical_failures / convergence_events, 1 / np.sqrt(convergence_events)


if __name__ == "__main__":
    from dotg.circuits import color_code, rotated_surface_code
    from dotg.decoders._syndrome_sampler import Sampler
    from dotg.noise import DepolarizingNoise

    noisy_circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(
        color_code(distance=5)
    )
    bp = BeliefPropagation(circuit=noisy_circuit, max_iterations=10)
    print(bp.logical_error(num_shots=1e3))
