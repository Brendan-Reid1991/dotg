"""This module provides an abstract base class for Belief Propagation based decoders."""
from abc import ABC
from enum import IntEnum
from typing import List

import numpy as np
import stim
from ldpc import bp_decoder
from numpy.typing import NDArray

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


class LDPC_BeliefPropagationDecoder(Decoder, ABC):
    """_summary_

    Parameters
    ----------
    circuit : stim.Circuit
        _description_
    max_iterations : int
        _description_
    message_updates : MessageUpdates | int
        _description_

    Raises
    ------
    ValueError
        _description_
    ValueError
        _description_
    """

    def __init__(
        self,
        circuit: stim.Circuit,
        max_iterations: int,
        message_updates: MessageUpdates | int,
    ):
        super().__init__(circuit=circuit)

        self.max_iterations = max_iterations
        self.message_updates = message_updates

        if not self.max_iterations > 0 or not isinstance(self.max_iterations, int):
            raise ValueError(
                "Max iterations needs to be positive and non-zero. "
                f"Received: {self.max_iterations}"
                ""
            )

        if self.message_updates not in [0, 1]:
            raise ValueError(
                "Message update kwarg must be one of 0 (product-sum) or 1 (minimum-sum)."
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

    @property
    def num_iterations(self) -> int:
        """Return the number of iterations it took for the BP algorithm to terminate.

        Returns
        -------
        int
        """
        return self._decoder.iter

    @property
    def posterior_log_probability_odds(self) -> List[float]:
        """Return the list of posterior log probability odds after the BP algorithm
        has ran. Returns all 0 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior log probability odds.
        """
        return self._decoder.log_prob_ratios

    @property
    def posterior_probability_odds(self) -> List[float]:
        """Return the list of posterior probability odds after the BP algorithm
        has ran. Returns all 1 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior probability odds.
        """
        return list(1 / np.exp(self.posterior_log_probability_odds))

    @property
    def posterior_probabilities(self) -> List[float]:
        """Return the list of posterior probabilities after the BP algorithm
        has ran. Returns all 0.5 if no decoding has taken place.

        Returns
        -------
        List[float]
            Posterior probabilities.
        """
        posterior_odds = self.posterior_probability_odds

        return [x / (1 + x) for x in posterior_odds]

    @property
    def converged(self) -> bool:
        return bool(self._decoder.converge)
