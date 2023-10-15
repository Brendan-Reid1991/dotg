from __future__ import annotations
from typing import Optional
import multiprocessing as mp
import numpy as np
from dotg.decoders._decoder_base_class import Decoder
from dotg.decoders._belief_propagation_base_class import LDPCBeliefPropagationDecoder


class DecoderManager:
    def __init__(self, decoder: Decoder, cores: Optional[int] = None) -> None:
        self.decoder = decoder
        self.cores = cores or mp.cpu_count()

    def _get_logical_error(self, num_shots: int | float):
        return self.decoder.logical_error(num_shots=num_shots)

    def run(self, num_shots: int | float):
        shots_per_core = num_shots // self.cores

        if isinstance(self.decoder, LDPCBeliefPropagationDecoder):
            raise ValueError("These must be parallelised manually.")

        with mp.Pool(processes=self.cores) as pool:
            results = pool.map(self._get_logical_error, [shots_per_core] * self.cores)
        return np.mean(results), np.std(results)
