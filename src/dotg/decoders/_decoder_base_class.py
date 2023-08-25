"""This module defines the decoder base class."""

from abc import ABC, abstractmethod

import stim
from dotg.utilities._syndrome_sampler import (
    NoNoiseInCircuitError,
    check_if_noisy_circuit,
)


class Decoder(ABC):
    """A decoder base class."""

    def __init__(self, circuit: stim.Circuit) -> None:
        self.circuit = circuit

        if not check_if_noisy_circuit(circuit=self.circuit):
            raise NoNoiseInCircuitError()

    @abstractmethod
    def logical_error(self, num_shots: int | float) -> float:
        """This method decodes a bulk of syndromes and returns the fraction of which
        resulted in a logical error.

        Parameters
        ----------
        num_shots : int | float
            Number of syndromes to sample.
        exclude_empty : bool
            Whether or not to exclude empty syndromes from the simulation, by default
            False.

        Returns
        -------
        float
            The logical error probability.
        """
        pass
