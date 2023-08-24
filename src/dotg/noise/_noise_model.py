"""This module defines a bespoke noise model class."""
from __future__ import annotations

from typing import Tuple, TypeAlias

import stim

from dotg.utilities import (MeasureAndReset, MeasurementGates, OneQubitGates,
                            OneQubitNoiseChannels, ResetGates, StimDecorators,
                            TwoQubitGates, TwoQubitNoiseChannels)

NoiseParam: TypeAlias = float | Tuple[float]


class NoiseModel:
    """Class that takes in specific noise channels and corresponding strengths, to be
    applied to a circuit.


        Parameters
        ----------
        two_qubit_gate_noise : Tuple[TwoQubitNoiseChannels, NoiseParam]
            Two qubit gate noise instruction.
        one_qubit_gate_noise : Tuple[OneQubitNoiseChannels, NoiseParam]
            One qubit gate noise instruction.
        reset_noise : Tuple[OneQubitNoiseChannels, NoiseParam]
            Reset noise instruction.
        measurement_noise : float
            Measurement noise value.

        Raises
        ------
        ValueError
            If float parameter passed does not lie in the range (0, 1).
        ValueError
            If the noise channel given is OneQubitNoiseChannels.PAULI_CHANNEL_1
            (equivalently TwoQubitNoiseChannels.PAULI_CHANNEL_2) and the parameter
            is not a tuple of length 3 (equivalently length 15).
        ValueError
            If the measurement flip value does not lie in the range (0, 1).

    """

    def __init__(
        self,
        two_qubit_gate_noise: Tuple[TwoQubitNoiseChannels, NoiseParam],
        one_qubit_gate_noise: Tuple[OneQubitNoiseChannels, NoiseParam],
        reset_noise: Tuple[OneQubitNoiseChannels, NoiseParam],
        measurement_noise: float,
    ) -> None:
        for _channel, _param in [
            two_qubit_gate_noise,
            one_qubit_gate_noise,
            reset_noise,
        ]:
            if isinstance(_param, float | int):
                if not 0 < _param < 1:
                    raise ValueError(
                        f"Invalid noise parameter passed for channel {_channel}: {_param}"
                    )
            if _channel in [
                OneQubitNoiseChannels.PAULI_CHANNEL_1,
                TwoQubitNoiseChannels.PAULI_CHANNEL_2,
            ] and ((not isinstance(_param, tuple)) or (len(_param) not in [3, 15])):
                raise ValueError(
                    "Stim noise channels `PAULI_CHANNEL_1` and `PAULI_CHANNEL_2` "
                    "must be accompanied with tuple of floats of lengths 3 and 15 "
                    "respectively."
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
                    name=self._reset_noise_channel.value,
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

            if instr.name in OneQubitGates.members():
                noisy_circuit.append(
                    name=self._one_qubit_gate_noise_channel.value,
                    targets=instr.targets_copy(),
                    arg=self._one_qubit_gate_noise_parameter,
                )

            if instr.name in ResetGates.members():
                noisy_circuit.append(
                    name=self._reset_noise_channel.value,
                    targets=instr.targets_copy(),
                    arg=self._reset_noise_parameter,
                )

            if instr.name in TwoQubitGates.members():
                noisy_circuit.append(
                    name=self._two_qubit_gate_noise_channel.value,
                    targets=instr.targets_copy(),
                    arg=self._two_qubit_gate_noise_parameter,
                )

        return noisy_circuit
