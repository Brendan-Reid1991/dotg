"""This module provides access to the pymatching decoding package."""
from pymatching import Matching
import stim
import numpy as np


class MinimumWeightPerfectMatching:
    """_summary_"""

    def __init__(self, circuit: stim.Circuit) -> None:
        self.circuit = circuit
        self.sampler = circuit.compile_detector_sampler()

        self.matching = Matching.from_detector_error_model(
            self.circuit.detector_error_model(
                approximate_disjoint_errors=True, decompose_errors=True
            )
        )

    def logical_error(self, num_shots: int):
        """_summary_

        Parameters
        ----------
        num_shots : int
            _description_

        Returns
        -------
        _type_
            _description_
        """
        syndrome_batch, observables = self.sampler.sample(
            shots=int(num_shots), separate_observables=True
        )
        self.matching.decode_batch(syndrome_batch[0:1, :])

        predicted_observables = self.matching.decode_batch(syndrome_batch)
        return np.sum(np.any(predicted_observables != observables, axis=1)) / num_shots
