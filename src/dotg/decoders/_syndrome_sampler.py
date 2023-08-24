"""This module provides functionality to get syndromes from a circuit."""
from __future__ import annotations

from typing import Any, List, Tuple

import numpy as np
import stim
from numpy.typing import NDArray

# pylint: disable=no-member


class Sampler:
    """_summary_"""

    def __init__(self, circuit: stim.Circuit) -> None:
        self.circuit = circuit

    def __call__(
        self, shots: int | float = 1000, exclude_empty: bool = False
    ) -> Tuple[NDArray[Any], List[bool]]:
        """Given a stim circuit, sample from the detectors and generate some syndromes.

        Parameters
        ----------
        circuit : stim.Circuit
            Circuit to sample from.
        shots : int, optional
            How many syndromes to generate, by default 1000.
        exclude_empty : bool, optional
            Whether to ignore zero-weight syndromes, by default False. If True,
            syndromes will be generated repeatedly until enough have been collected.

        Returns
        -------
        Tuple[NDArray[Any], List[np.bool]]
            A tuple of iterables:
                - The first element is an array of syndromes, of dimension
                (shots * num_detectors). In each row, 1 (0) indicates detector did (not)
                trigger.
                - The second element is an list of booleans, of dimension (shots * 1).
                These indicate whether the syndrome in the row triggered the logical
                observable.
        """
        detector_sampler = self.circuit.compile_detector_sampler()
        syndrome_batch: List[List[int]] = []
        observable_batch: List[bool] = []

        if exclude_empty:
            while len(syndrome_batch) < shots:
                _syndrome_batch, _observable_batch = detector_sampler.sample(
                    shots=int(shots), separate_observables=True
                )
                for _syn, _ob in zip(_syndrome_batch, _observable_batch):
                    if any(_syn):
                        syndrome_batch.append(_syn)
                        observable_batch.append(_ob)
        else:
            syndrome_batch, observable_batch = detector_sampler.sample(
                shots=int(shots), separate_observables=True
            )

        return (
            np.asarray([[int(bit) for bit in syndrome] for syndrome in syndrome_batch])[
                0 : int(shots)
            ],
            observable_batch[0 : int(shots)],
        )
