from __future__ import annotations
from typing import Tuple
import stim

from dotg.utilities import (
    OneQubitNoiseChannels,
    TwoQubitNoiseChannels,
    StimDecorators,
    OneQubitGates,
    TwoQubitGates,
    ResetGates,
    MeasurementGates,
    MeasureAndReset,
)


class NoiseModel:
    """Class that takes in specific noise channels and corresponding strengths, to be
    applied to a circuit.


        Parameters
        ----------
        two_qubit_gate_noise : Tuple[TwoQubitNoiseChannels, float]
            Two qubit gate noise instruction.
        one_qubit_gate_noise : Tuple[OneQubitNoiseChannels, float]
            One qubit gate noise instruction.
        reset_noise : Tuple[OneQubitNoiseChannels, float]
            Reset noise instruction.
        measurement_noise : float
            Measurement noise value.

        Raises
        ------
        ValueError
            If, for each of two_qubit_gate_noise, one_qubit_gate_noise and reset_noise,:
                - the first element is not in either OneQubitNoiseChannels or
                TwoQubitNoiseChannels
                - the second element does not lie in the range (0, 1).
        ValueError
            If the measurement flip value does not lie in the range (0, 1).

    """

    def __init__(
        self,
        two_qubit_gate_noise: Tuple[TwoQubitNoiseChannels, float],
        one_qubit_gate_noise: Tuple[OneQubitNoiseChannels, float],
        reset_noise: Tuple[OneQubitNoiseChannels, float],
        measurement_noise: float,
    ) -> None:
        if not all(
            ((x in OneQubitNoiseChannels) | (x in TwoQubitNoiseChannels)) and 0 < y < 1
            for x, y in zip(*[two_qubit_gate_noise, one_qubit_gate_noise, reset_noise])
        ):
            raise ValueError(
                "Invalid noise channel and tuple pair passed. Either channel is not "
                "permitted or parameter is outside (0, 1) range. Received:\n"
                f"  two_qubit_gate_noise: {two_qubit_gate_noise},\n"
                f"  one_qubit_gate_noise: {one_qubit_gate_noise},\n"
                f"  reset_noise: {reset_noise}."
            )

        if not 0 < measurement_noise < 1:
            raise ValueError(
                f"Invalid measurement flip value given: {measurement_noise}"
            )
        (
            self._two_qubit_gate_noise_channel,
            self._two_qubit_gate_noise_parameter,
        ) = two_qubit_gate_noise

        (
            self._one_qubit_gate_noise_channel,
            self._one_qubit_gate_noise_parameter,
        ) = one_qubit_gate_noise

        (
            self._reset_noise_channel,
            self._reset_noise_parameter,
        ) = reset_noise

        self._measurement_noise_parameter = measurement_noise

    def permute_circuit(self, circuit: stim.Circuit) -> stim.Circuit:
        """Given an input circuit without noise, apply this noise model to the circuit.

        Parameters
        ----------
        circuit : stim.Circuit
            An input noiseless circuit.

        Returns
        -------
        stim.Circuit
            The same circuit with noise applied appropriately.
        """

        noisy_circuit = stim.Circuit()
        for instr in circuit:
            if instr.name in MeasureAndReset.members():
                noisy_circuit.append(
                    name=MeasurementGates.MZ.value,
                    targets=instr.targets_copy(),
                    arg=self._measurement_noise_parameter,
                )
                noisy_circuit.append(
                    name=ResetGates.RZ.value, targets=instr.targets_copy()
                )
                noisy_circuit.append(
                    name=self._one_qubit_gate_noise_channel.value,
                    targets=instr.targets_copy(),
                    arg=self._reset_noise_parameter,
                )
                continue

            if instr.name in MeasurementGates.members():
                noisy_circuit.append(
                    name=instr.name,
                    targets=instr.targets_copy(),
                    arg=self._measurement_noise_parameter,
                )
                continue

            noisy_circuit.append(instr)
            if instr.name in StimDecorators.members():
                continue

            if instr.name in OneQubitGates.members() + ResetGates.members():
                noisy_circuit.append(
                    name=self._one_qubit_gate_noise_channel,
                    targets=instr.targets_copy(),
                    arg=self._one_qubit_gate_noise_parameter,
                )

            if instr.name in TwoQubitGates.members():
                noisy_circuit.append(
                    name=self._two_qubit_gate_noise_channel,
                    targets=instr.targets_copy(),
                    arg=self._two_qubit_gate_noise_parameter,
                )

        return noisy_circuit
