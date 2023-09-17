from typing import List, Tuple
from numpy.typing import NDArray
from dotg.decoders._decoder_base_class import Decoder
from dotg.decoders._belief_propagation_base_class import (
    LDPC_DecoderOptions,
    MessageUpdates,
)
from dotg.decoders import MinimumWeightPerfectMatching, BeliefPropagation
from dotg.utilities import Sampler
import numpy as np

import stim


class Partial_BP_MWPM(Decoder):
    def __init__(
        self,
        circuit: stim.Circuit,
        decoder_options: LDPC_DecoderOptions = LDPC_DecoderOptions(
            max_iterations=10, message_updates=MessageUpdates.PROD_SUM
        ),
        hard_decision_tolerance: float = 0.5,
    ) -> None:
        super().__init__(circuit=circuit)
        self.decoder_options = decoder_options

        self._first_stage_decoder = BeliefPropagation(
            circuit=self.circuit, decoder_options=self.decoder_options
        )

        self._second_stage_decoder = MinimumWeightPerfectMatching(circuit=self.circuit)

        self.hard_decision_tolerance = hard_decision_tolerance

        self._first_stage_converged: bool = False

        if not 0 < self.hard_decision_tolerance <= 1:
            raise ValueError("Tolerance for hard decisions must be in the range (0, 1].")

    @property
    def converged(self) -> bool:
        return self._first_stage_converged

    @converged.setter
    def converged(self, replacement: bool):
        self._first_stage_converged = replacement

    def hard_decision(self, syndrome: List[int] | NDArray) -> Tuple[NDArray, NDArray]:
        posterior_probs = self._first_stage_decoder.posterior_probabilities

        _selection = [
            idx
            for idx, x in enumerate(posterior_probs)
            if x >= self.hard_decision_tolerance
        ]
        committed_errors = np.zeros(len(posterior_probs))
        committed_errors[_selection] = 1

        return (
            committed_errors,
            self._first_stage_decoder.update_syndrome_from_error_pattern(
                syndrome=np.asarray(syndrome), error_pattern=committed_errors
            ),
        )

    def decode_syndrome(self, syndrome: List[int] | NDArray) -> List[int] | NDArray:
        self.converged = False
        (
            converged,
            error_pattern,
            _,
        ) = self._first_stage_decoder.decode_syndrome(syndrome=syndrome)

        if converged:
            self.converged = True
            return error_pattern

        committed_errors, remaining_syndrome = self.hard_decision(syndrome=syndrome)

        if not any(remaining_syndrome):
            self.converged = True
            return committed_errors

        return self._second_stage_decoder.decode_syndrome(syndrome=remaining_syndrome)

    def logical_error(
        self, num_shots: int | float, exclude_empty: bool = False
    ) -> float:
        return 0


if __name__ == "__main__":
    from dotg.circuits.quantum_memory import SurfaceCode
    from dotg.noise import DepolarizingNoise
    import tqdm

    SHOTS = 1000

    circuit = DepolarizingNoise(physical_error=1e-2).permute_circuit(
        circuit=SurfaceCode.Rotated(distance=5).circuit
    )
    sampler = Sampler(circuit=circuit)
    syndromes, logicals = sampler(num_shots=SHOTS, exclude_empty=True)

    decoder = Partial_BP_MWPM(
        circuit=circuit,
        decoder_options=LDPC_DecoderOptions(
            max_iterations=30, message_updates=MessageUpdates.PROD_SUM
        ),
        hard_decision_tolerance=0.9,
    )

    convergence_rate: float = 0
    for syn, log in tqdm.tqdm(zip(syndromes, logicals)):
        error_pattern = decoder.decode_syndrome(syndrome=syn)
        # print(decoder.converged)
        if decoder.converged:
            convergence_rate += 1 / SHOTS

    print(convergence_rate)
