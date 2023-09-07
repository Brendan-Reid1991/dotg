"""This module defines the decoder base class."""
from abc import ABC, abstractmethod
from typing import List

import stim
from numpy.typing import NDArray

from dotg.utilities._syndrome_sampler import (NoNoiseInCircuitError,
                                              check_if_noisy_circuit)


class Decoder(ABC):
    """A decoder base class.


    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit defining our experiment.

    Raises
    ------
    NoNoiseInCircuitError
        If the circuit has no noise entries.
    """

    def __init__(self, circuit: stim.Circuit) -> None:
        self.circuit = circuit

        if not check_if_noisy_circuit(circuit=self.circuit):
            raise NoNoiseInCircuitError()

    @abstractmethod
    def decode_syndrome(self, syndrome: List[int] | NDArray) -> NDArray | List[int]:
        """Decode a single syndrome and return a corresponding error pattern that gives
        such a syndrome.

        Parameters
        ----------
        syndrome : List[int] | NDArray
            Syndrome to decode.


        Returns
        -------
        NDArray | List[int]
            An error pattern that results in the given syndrome
        """

    @abstractmethod
    def logical_error(self, num_shots: int | float) -> float:
        """Decode a bulk of syndromes and return the fraction of which
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
