"""The DecoderManager class allows for parallelisation of decoding jobs."""

from __future__ import annotations
from typing import Optional, Type, Tuple

import multiprocessing as mp
from functools import partial
import stim

import numpy as np
from dotg.decoders._decoder_base_classes._decoder_base_class import Decoder


class DecoderManager:
    """The Decoder Manager for parallelising decoding jobs.

    Takes as input the Decoder class, number of cores to
    parallelise over (optionally) and any other decoder options.

    Parameters
    ----------
    decoder: Type[Decoder]
        Decoder class.
    cores: Optional[int]
        Optional input for the number of cores to parallelise over.
        Defaults to the half the maximum number of cores on the machine.

    Methods
    -------
    run
        Run the parallelisation process by providing a noisy stim circuit,
        and the number of shots to sample.
    """

    def __init__(
        self, decoder: Type[Decoder], cores: Optional[int] = None, **kwargs
    ) -> None:
        self.decoder = decoder
        self.cores = cores or mp.cpu_count() // 2
        self._kwargs = kwargs

    def _logical_error(
        self, circuit: stim.Circuit, num_shots: int | float, **kwargs
    ) -> float:
        """A top level function for retrieving the logical error rate.
        Necessary in order to sidestep pickling issues.

        Parameters
        ----------
        circuit : stim.Circuit
            Noisy stim circuit.
        num_shots : int | float
            Number of shots to sample.

        Returns
        -------
        float
            Logical error probability.
        """
        return self.decoder(circuit=circuit, **kwargs).logical_error(
            num_shots=num_shots
        )

    def run(self, circuit: stim.Circuit, num_shots: int | float) -> Tuple[float, float]:
        """Parallelise the decoder on the given circuit and for the specified number of shots.

        Parameters
        ----------
        circuit : stim.Circuit
            Noisy stim circuit.
        num_shots : int | float
            Number of shots to sample.

        Returns
        -------
        Tuple[float, float]
            The mean and standard deviation of the logical error.
        """
        shots_per_core = num_shots // self.cores

        with mp.Pool(self.cores) as pool:
            results = pool.map(
                partial(
                    self._logical_error,
                    circuit,
                    **self._kwargs,
                ),
                [shots_per_core] * self.cores,
            )
        return float(np.mean(results)), float(np.std(results))
