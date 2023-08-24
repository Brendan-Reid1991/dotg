"""This module provides a class function to convert a circuit into a parity check matrix,
logical check matrix, and a vector of individual probabilities for each error 
mechanism."""
from typing import List, TypeAlias

import numpy as np
import stim

# pylint: disable=invalid-name
ArrayT: TypeAlias = List[List[float]]


class CircuitUnderstander:
    """The Circuit Understander has logged on.

    This class takes as input a stim circuit and automatically calculates the parity
    check matrix, logical check matrix and the probabilities of each error.

    Parameters
    ----------
    circuit : stim.Circuit
        Stim circuit describing our experiment.
    decompose_errors : bool, optional
        Whether or not to decompose the errors into graphlike errors, by default False.

    Attributes
    ----------
    parity_check : NDArray
        The parity check matrix of the circuit as a numpy.NDArray object. Element
        H[i, j] = 1 iff detector i anticommutes with error mechanism j, and 0 otherwise.
    logical_check : NDArray
        The logical check matrix of the circuit as numpy.NDArray object. Element
        L[i, j] = 1 iff logical observable i anticommutes with error mechanism j, and
        0 otherwise.
    error_probabilities : List[float]
        The list of probabilities relating to each error mechanism.
    """

    def __init__(self, circuit: stim.Circuit, decompose_errors: bool = False) -> None:
        self._understand_circuit(
            circuit=circuit.flattened(), decompose_errors=decompose_errors
        )

    @property
    def parity_check(self) -> ArrayT:
        """Returns the parity check matrix."""
        return self._parity

    @parity_check.setter
    def parity_check(self, new_parity: ArrayT):
        self._parity = new_parity

    @property
    def logical_check(self) -> ArrayT:
        """Returns the logical check matrix."""
        return self._logical

    @logical_check.setter
    def logical_check(self, new_logical: ArrayT):
        self._logical = new_logical

    @property
    def error_probabilities(self) -> List[float]:
        """Return a list of relative error probabilities."""
        return self._probs

    @error_probabilities.setter
    def error_probabilities(self, new_probabilities: List[float]):
        self._probs = new_probabilities

    def _understand_circuit(
        self, circuit: stim.Circuit, decompose_errors: bool = False
    ):
        """Inspect the input circuit and get the parity check, logical check and error
        probabilities."""
        dem = circuit.detector_error_model(decompose_errors=decompose_errors)

        parity_check = np.zeros((dem.num_detectors, dem.num_errors))
        logical_check = np.zeros((dem.num_observables, dem.num_errors))
        error_probabilities = []

        for idx, event in enumerate(dem):
            if event.type != "error":
                continue

            detectors_trigged = [
                x.val for x in event.targets_copy() if x.is_relative_detector_id()
            ]
            logicals_triggered = set(
                x.val for x in event.targets_copy() if x.is_logical_observable_id()
            )
            for detector in detectors_trigged:
                parity_check[detector, idx] = 1
            for logical in logicals_triggered:
                logical_check[logical, idx] = 1

            error_probabilities.append(event.args_copy()[0])

        self.parity_check = list(parity_check)
        self.logical_check = list(logical_check)
        self.error_probabilities = error_probabilities
