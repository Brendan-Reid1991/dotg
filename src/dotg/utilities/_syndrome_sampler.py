"""This module provides functionality to get syndromes from a circuit."""

from __future__ import annotations

from typing import Any, List, Tuple

import numpy as np
import stim
from numpy.typing import NDArray

from dotg.utilities.stim_assets import (
    MeasurementGates,
    OneQubitNoiseChannels,
    TwoQubitNoiseChannels,
)

# pylint: disable=no-member


class NoNoiseInCircuitError(ValueError):
    """Error to highlight when circuits contain no error messages."""

    def __init__(self) -> None:
        self.message = "Circuit passed has no noise; decoding will have no effect."
        super().__init__(self.message)


def check_if_noisy_circuit(circuit: stim.Circuit) -> bool:
    """Check if the given stim circuit has noise entries.

    Parameters
    ----------
    circuit : stim.Circuit
        stim circuit.

    Returns
    -------
    bool
        Whether the circuit has noise entries.
    """
    if any(
        instr.name in OneQubitNoiseChannels.members() + TwoQubitNoiseChannels.members()
        for instr in circuit
    ) or any(
        any(x > 0 for x in instr.gate_args_copy())
        for instr in circuit
        if instr.name in MeasurementGates.members()
    ):
        return True

    return False


class Sampler:
    """This class allows you to sample syndromes from a given stim circuit."""

    def __init__(self, circuit: stim.Circuit) -> None:
        self.circuit = circuit

    def __call__(
        self, num_shots: int | float = 1000, exclude_empty: bool = False
    ) -> Tuple[NDArray[Any], List[bool]]:
        """Given a stim circuit, sample from the detectors and generate some syndromes.

        TODO modify this from a __call__ functionality, as I've really gone off it.

        Parameters
        ----------
        circuit : stim.Circuit
            Circuit to sample from.
        num_shots : int, optional
            How many syndromes to generate, by default 1000.
        exclude_empty : bool, optional
            Whether to ignore zero-weight syndromes, by default False. If True,
            syndromes will be generated repeatedly until enough have been collected.

        Returns
        -------
        Tuple[NDArray[Any], List[np.bool_]]
            A tuple of iterables:
                - The first element is an array of syndromes, of dimension
                (num_shots * num_detectors). In each row, 1 (0) indicates detector did
                (not) trigger.
                - The second element is an list of booleans, of dimension
                (num_shots * 1). These indicate whether the syndrome in the row triggered
                the logical observable.

        Raises
        ------
        NoNoiseInCircuitError
            If there are no noisy entries in the stim circuit.
        """
        if not check_if_noisy_circuit(circuit=self.circuit):
            raise NoNoiseInCircuitError()

        detector_sampler = self.circuit.compile_detector_sampler()

        if exclude_empty:
            syndrome_batch: List[List[int]] = []
            observable_batch: List[bool] = []
            while len(syndrome_batch) < num_shots:
                _syndrome_batch, _observable_batch = detector_sampler.sample(
                    shots=int(num_shots), separate_observables=True
                )
                for _syn, _ob in zip(_syndrome_batch, _observable_batch):
                    if any(_syn):
                        syndrome_batch.append(_syn)
                        observable_batch.append(_ob)
        else:
            syndrome_batch, observable_batch = detector_sampler.sample(
                shots=int(num_shots), separate_observables=True
            )

        return (
            np.asarray([[int(bit) for bit in syndrome] for syndrome in syndrome_batch])[
                0 : int(num_shots)
            ],
            observable_batch[0 : int(num_shots)],
        )
