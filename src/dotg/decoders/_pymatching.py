"""This module provides access to the Minimum Weight Perfect Matching (MWPM) decoder via 
the pymatching package: https://github.com/oscarhiggott/PyMatching"""
from __future__ import annotations

from typing import List

import numpy as np
import stim
from numpy.typing import NDArray
from pymatching import Matching

from dotg.decoders._decoder_base_class import Decoder


class MinimumWeightPerfectMatching(Decoder):
    """This class allows decoding on graphs via the Minimum Weight Perfect Matching
    algorithm. Due to the functionality of the pymatching package, this class requires
    no other dependencies to generate a logical error value from an input circuit.

    Parameters
    ----------
    circuit : stim.Circuit
        stim circuit to evaluate the decoder on.

    Raises
    ------
    ValueError
        If the circuit passed has no noise entries.
    ValueError
        If the circuit passed does not permit a graph-like error model.
    ValueError
        If building the pymatching.Matching object fails for any other reason.
    """

    def __init__(self, circuit: stim.Circuit) -> None:
        super().__init__(circuit=circuit)
        self.sampler = circuit.compile_detector_sampler()

        try:
            self.matching = Matching.from_detector_error_model(
                self.circuit.detector_error_model(
                    approximate_disjoint_errors=True, decompose_errors=True
                )
            )
        except ValueError as exc:
            if "Failed to decompose" in exc.args[0]:
                raise ValueError(
                    "Circuit passed does not permit a graph-like error model, "
                    "which MWPM requires."
                ) from exc

    def decode_syndrome(self, syndrome: List[int] | NDArray) -> NDArray | List[int]:
        return self.matching.decode(syndrome)

    def logical_error(self, num_shots: int | float) -> float:
        syndrome_batch, observables = self.sampler.sample(
            shots=int(num_shots), separate_observables=True
        )
        # Cache the graph for speed
        self.matching.decode_batch(syndrome_batch[0:1, :])

        predicted_observables = self.matching.decode_batch(syndrome_batch)
        return np.sum(np.any(predicted_observables != observables, axis=1)) / num_shots
