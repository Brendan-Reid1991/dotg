"""This module defines a bespoke noise model class."""
from __future__ import annotations

from typing import List, Optional, Tuple, Type, TypeAlias

import stim

from dotg.utilities import get_circuit_layers
from dotg.utilities.stim_assets import (
    MeasureAndReset,
    MeasurementGates,
    OneQubitGates,
    OneQubitNoiseChannels,
    ResetGates,
    StimDecorators,
    TwoQubitGates,
    TwoQubitNoiseChannels,
)

NoiseParamT: TypeAlias = float | Tuple[float]
NoiseChannelT: TypeAlias = TwoQubitNoiseChannels | OneQubitNoiseChannels


class NoiseModel:
    """Class that takes in specific noise channels and corresponding strengths, to be
    applied to a circuit.

    TODO: Split into smaller components, and add functionality for idle noise.

        Parameters
        ----------
        two_qubit_gate_noise : Tuple[TwoQubitNoiseChannels, NoiseParam]
            Two qubit gate noise instruction.
        one_qubit_gate_noise : Tuple[OneQubitNoiseChannels, NoiseParam]
            One qubit gate noise instruction.
        reset_noise : Tuple[OneQubitNoiseChannels, NoiseParam]
            Reset noise instruction.
        idle_noise : Tuple[OneQubitNoiseChannels, NoiseParam]
            Idle noise instruction.
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
        two_qubit_gate_noise: Optional[Tuple[NoiseChannelT, NoiseParamT]] = None,
        one_qubit_gate_noise: Optional[Tuple[NoiseChannelT, NoiseParamT]] = None,
        reset_noise: Optional[Tuple[NoiseChannelT, NoiseParamT]] = None,
        idle_noise: Optional[Tuple[NoiseChannelT, NoiseParamT]] = None,
        measurement_noise: float = 0,
    ) -> None:
        # HouseKeeping

        two_qubit_gate_noise = (
            (TwoQubitNoiseChannels.DEPOLARIZE2, 0)
            if two_qubit_gate_noise is None
            else two_qubit_gate_noise
        )
        one_qubit_gate_noise = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if one_qubit_gate_noise is None
            else one_qubit_gate_noise
        )
        reset_noise = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if reset_noise is None
            else reset_noise
        )

        idle_noise = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if idle_noise is None
            else idle_noise
        )

        for _channel, _param in [
            two_qubit_gate_noise,
            one_qubit_gate_noise,
            reset_noise,
            idle_noise,
        ]:
            if isinstance(_param, float | int):
                if not 0 <= _param < 1:
                    raise ValueError(
                        f"Invalid noise parameter passed for channel {_channel}: {_param}"
                    )
            if _channel in [
                OneQubitNoiseChannels.PAULI_CHANNEL_1,
                TwoQubitNoiseChannels.PAULI_CHANNEL_2,
            ] and ((not isinstance(_param, tuple)) or (len(_param) not in [3, 15])):
                raise ValueError(
                    "stim noise channels `PAULI_CHANNEL_1` and `PAULI_CHANNEL_2` "
                    "must be accompanied with tuple of floats of lengths 3 and 15 "
                    "respectively."
                )

        if not 0 <= measurement_noise < 1:
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

        (
            self._idle_noise_channel,
            self._idle_noise_parameter,
        ) = idle_noise

        self._measurement_noise_parameter = measurement_noise

    def _measurement_instruction(
        self, circuit: stim.Circuit, instruction: stim.CircuitInstruction
    ) -> stim.Circuit:
        circuit.append(
            name=instruction.name,
            targets=instruction.targets_copy(),
            arg=self._measurement_noise_parameter,
        )
        return circuit

    def _measurement_and_reset_instruction(
        self, circuit: stim.Circuit, instruction: stim.CircuitInstruction
    ) -> stim.Circuit:
        circuit.append(
            name=MeasurementGates.MZ,
            targets=instruction.targets_copy(),
            arg=self._measurement_noise_parameter,
        )
        circuit.append(name=ResetGates.RZ, targets=instruction.targets_copy())
        if self._reset_noise_parameter:
            circuit.append(
                name=self._reset_noise_channel,
                targets=instruction.targets_copy(),
                arg=self._reset_noise_parameter,
            )
        return circuit

    def _gate_instruction(
        self, circuit: stim.Circuit, instruction: stim.CircuitInstruction
    ) -> stim.Circuit:
        if (
            instruction.name in OneQubitGates.members()
            and self._one_qubit_gate_noise_parameter
        ):
            circuit.append(
                name=self._one_qubit_gate_noise_channel,
                targets=instruction.targets_copy(),
                arg=self._one_qubit_gate_noise_parameter,
            )

        if (
            instruction.name in TwoQubitGates.members()
            and self._two_qubit_gate_noise_parameter
        ):
            circuit.append(
                name=self._two_qubit_gate_noise_channel,
                targets=instruction.targets_copy(),
                arg=self._two_qubit_gate_noise_parameter,
            )

        if instruction.name in ResetGates.members() and self._reset_noise_parameter:
            circuit.append(
                name=self._reset_noise_channel,
                targets=instruction.targets_copy(),
                arg=self._reset_noise_parameter,
            )

        return circuit

    def add_idle_noise(self, circuit: stim.Circuit) -> stim.Circuit:
        qubit_indices = set(
            next(x.value for x in line.targets_copy())
            for line in circuit
            if line.name == StimDecorators.QUBIT_COORDS
        )
        circuit_layers = get_circuit_layers(circuit=circuit)

        final_circuit = stim.Circuit()
        for timeslice in circuit_layers:
            active_qubits = set(
                x.value
                for instr in timeslice
                for x in instr.targets_copy()
                if instr.name
            )

            idle_qubits = qubit_indices - active_qubits
            if idle_qubits and self._idle_noise_parameter:
                new_timeslice, tick = timeslice[0:-1], timeslice[-1]
                new_timeslice.append(
                    name=self._idle_noise_channel,
                    targets=idle_qubits,
                    arg=self._idle_noise_parameter,
                )
                new_timeslice.append(name=tick)
                timeslice = new_timeslice
            final_circuit += timeslice
        return final_circuit

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
                self._measurement_and_reset_instruction(
                    circuit=noisy_circuit, instruction=instr
                )
                continue

            if instr.name in MeasurementGates.members():
                noisy_circuit = self._measurement_instruction(
                    circuit=noisy_circuit, instruction=instr
                )
                continue

            noisy_circuit.append(instr)
            if instr.name in StimDecorators.members():
                continue

            noisy_circuit = self._gate_instruction(
                circuit=noisy_circuit, instruction=instr
            )

        return noisy_circuit
