from __future__ import annotations
from typing import Optional
import multiprocessing as mp
import numpy as np
from dotg.decoders import BPOSD, LDPCDecoderOptions, OSDMethods
from dotg.decoders._decoder_base_class import Decoder
from dotg.decoders._belief_propagation_base_class import LDPCBeliefPropagationDecoder

from dotg.circuits import SurfaceCode
from dotg.noise import DepolarizingNoise

code = SurfaceCode.Rotated(distance=5)
circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(code.memory)


class DecoderManager:
    def __init__(self, decoder: Decoder, cores: Optional[int] = None) -> None:
        self.decoder = decoder
        self.cores = cores or mp.cpu_count()

    def _parallelise_cython(self, num_shots: int | float):
        decoder = BPOSD(
            circuit=circuit,
            decoder_options=LDPCDecoderOptions(
                max_iterations=5, osd_method=OSDMethods.EXHAUSTIVE
            ),
        )
        return decoder.logical_error(num_shots=num_shots)

    def run(self, num_shots: int | float):
        shots_per_core = num_shots // self.cores

        if isinstance(self.decoder, LDPCBeliefPropagationDecoder):
            with mp.Pool(self.cores) as pool:
                results = pool.map(
                    self._parallelise_cython,
                    [shots_per_core] * self.cores,
                )
            return np.mean(results), np.std(results)

        with mp.Pool(self.cores) as pool:
            results = pool.map(self.decoder.logical_error, [shots_per_core] * self.cores)
        return np.mean(results), np.std(results)


if __name__ == "__main__":
    from dotg.decoders import (
        BPOSD,
        LDPCDecoderOptions,
        OSDMethods,
        MinimumWeightPerfectMatching,
    )
    from dotg.decoders._manager import DecoderManager
    from dotg.circuits import SurfaceCode
    from dotg.noise import DepolarizingNoise

    code = SurfaceCode.Rotated(distance=5)
    circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(code.memory)

    # decoder = BPOSD(
    #     circuit=circuit,
    #     decoder_options=LDPCDecoderOptions(
    #         max_iterations=5, osd_method=OSDMethods.EXHAUSTIVE
    #     ),
    # )
    decoder = MinimumWeightPerfectMatching(circuit=circuit)

    manager = DecoderManager(decoder=decoder)

    print(manager.run(num_shots=int(1e4)))
