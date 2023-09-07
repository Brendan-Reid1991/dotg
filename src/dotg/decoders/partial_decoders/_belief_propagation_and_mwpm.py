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
        self.converged = self._first_stage_decoder.converged

        self._second_stage_decoder = MinimumWeightPerfectMatching(circuit=self.circuit)

        self.hard_decision_tolerance = hard_decision_tolerance

        if not 0 < self.hard_decision_tolerance <= 1:
            raise ValueError("Tolerance for hard decisions must be in the range (0, 1].")

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
        (
            converged,
            error_pattern,
            _,
        ) = self._first_stage_decoder.decode_syndrome(syndrome=syndrome)

        if converged:
            return error_pattern

        committed_errors, remaining_syndrome = self.hard_decision(syndrome=syndrome)

        if not any(remaining_syndrome):
            return committed_errors

        return self._second_stage_decoder.decode_syndrome(syndrome=remaining_syndrome)

    def logical_error(
        self, num_shots: int | float, exclude_empty: bool = False
    ) -> float:
        return 0

    #     sampler = Sampler(circuit=self.circuit)
    #     syndromes, logicals = sampler(num_shots=num_shots, exclude_empty=exclude_empty)

    #     convergence_events: int = 0
    #     remaining_syndromes: List[NDArray] = []
    #     logical_failures: int = 0


if __name__ == "__main__":
    from dotg.circuits import rotated_surface_code
    from dotg.noise import DepolarizingNoise

    SHOTS = 1000

    circuit = DepolarizingNoise(physical_error=1e-3).permute_circuit(
        circuit=rotated_surface_code(distance=5)
    )
    sampler = Sampler(circuit=circuit)
    syndromes, logicals = sampler(num_shots=SHOTS, exclude_empty=True)

    decoder = Partial_BP_MWPM(
        circuit=circuit,
        decoder_options=LDPC_DecoderOptions(
            max_iterations=30, message_updates=MessageUpdates.PROD_SUM
        ),
        hard_decision_tolerance=0.5,
    )

    convergence_rate: float = 0
    for syn, log in zip(syndromes, logicals):
        error_pattern = decoder.decode_syndrome(syndrome=syn)
        # print(decoder.converged)
        if decoder.converged:
            convergence_rate += 1 / SHOTS

    print(convergence_rate)
