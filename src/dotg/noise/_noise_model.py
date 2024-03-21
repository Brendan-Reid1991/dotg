"""This module defines a bespoke noise model class."""

from __future__ import annotations

from typing import Optional, Tuple, TypeAlias

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

NoiseParam: TypeAlias = float | Tuple[float]
NoiseChannel: TypeAlias = TwoQubitNoiseChannels | OneQubitNoiseChannels

# pylint: disable=unused-argument, too-many-instance-attributes


class NoiseModel:
    """Class that takes in specific noise channels and corresponding strengths, to be
    applied to a circuit.

    NOTE: If your circuit does not have defined qubit coordinates, you will be unable to
    add idle noise.

    Parameters
    ----------
    two_qubit_gate_noise : Tuple[NoiseChannel, NoiseParam], optional
        Two qubit gate noise instruction, by default None.
    one_qubit_gate_noise : Tuple[NoiseChannel, NoiseParam], optional
        One qubit gate noise instruction.
    reset_noise : Tuple[NoiseChannel, NoiseParam], optional
        Reset noise instruction.
    idle_noise : Tuple[NoiseChannel, NoiseParam], optional
        Idle noise instruction.
    measurement_noise : float, optional
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
        two_qubit_gate_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        one_qubit_gate_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        reset_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        idle_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        measurement_noise: float = 0,
    ) -> None:
        # HouseKeeping

        self._is_legal_noise_model(
            two_qubit_gate_noise=two_qubit_gate_noise,
            one_qubit_gate_noise=one_qubit_gate_noise,
            reset_noise=reset_noise,
            idle_noise=idle_noise,
            measurement_noise=measurement_noise,
        )

        (self._two_qubit_gate_noise_channel, self._two_qubit_gate_noise_parameter) = (
            (TwoQubitNoiseChannels.DEPOLARIZE2, 0)
            if two_qubit_gate_noise is None
            else two_qubit_gate_noise
        )
        (self._one_qubit_gate_noise_channel, self._one_qubit_gate_noise_parameter) = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if one_qubit_gate_noise is None
            else one_qubit_gate_noise
        )
        (self._reset_noise_channel, self._reset_noise_parameter) = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if reset_noise is None
            else reset_noise
        )

        (self._idle_noise_channel, self._idle_noise_parameter) = (
            (OneQubitNoiseChannels.DEPOLARIZE1, 0.0)
            if idle_noise is None
            else idle_noise
        )

        self._measurement_noise_parameter = measurement_noise

    def _is_legal_noise_model(
        self,
        two_qubit_gate_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        one_qubit_gate_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        reset_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        idle_noise: Optional[Tuple[NoiseChannel, NoiseParam]] = None,
        measurement_noise: float = 0,
    ):
        """Run tests on all the inputs to make sure it's a legal noise model."""

        # Check quantum gate channels first
        for _arg_name, _arg in locals().items():
            if (_arg in (None, self)) or _arg_name == "measurement_noise":
                continue
            _channel, _param = _arg
            if (
                _arg_name == "two_qubit_gate_noise"
                and _channel not in TwoQubitNoiseChannels.members()
            ) or (
                _arg_name != "two_qubit_gate_noise"
                and _channel not in OneQubitNoiseChannels.members()
            ):
                raise ValueError(
                    f"Invalid gate/noise pairing: {_arg_name} - {_channel}"
                )

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

    def _measurement_instruction(
        self, circuit: stim.Circuit, instruction: stim.CircuitInstruction
    ) -> stim.Circuit:
        """Add a measurement instruction (with noise) to the end of the given circuit.
        If the `instruction` kwarg is actually a measurement and reset instruction, the
        relevant method is called instead.

        Parameters
        ----------
        circuit : stim.Circuit
            stim circuit
        instruction : stim.CircuitInstruction
            measurement instruction.

        Returns
        -------
        stim.Circuit
            The circuit with the measurement instruction appended.
        """
        if instruction.name == "MR":
            return self._measurement_and_reset_instruction(
                circuit=circuit, instruction=instruction
            )

        circuit.append(
            name=instruction.name,
            targets=instruction.targets_copy(),
            arg=self._measurement_noise_parameter,
        )
        return circuit

    def _measurement_and_reset_instruction(
        self, circuit: stim.Circuit, instruction: stim.CircuitInstruction
    ) -> stim.Circuit:
        """Add a measurement and reset instruction (with noise) to a stim circuit, but
        in separate steps and with a TICK command in beteween.

        Parameters
        ----------
        circuit : stim.Circuit
            stim circuit
        instruction : stim.CircuitInstruction
            measurement and reset stim instruction.

        Returns
        -------
        stim.Circuit
            The circuit with the measurement and reset instruction appended.
        """
        circuit.append(
            name=MeasurementGates.MZ,
            targets=instruction.targets_copy(),
            arg=self._measurement_noise_parameter,
        )
        circuit.append(name=StimDecorators.TICK)
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
        """Add a noise entry to a stim circuit right after a gate instruction.

        Parameters
        ----------
        circuit : stim.Circuit
            stim Circuit.
        instruction : stim.CircuitInstruction
            Instruction explaining what gate has been applied and to which qubits.

        Returns
        -------
        stim.Circuit
            The circuit with the gate now applied noisily.
        """
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
        """Add idle noise to a circuit. This method divides the circuit into congruent
        layers (equivalently, timeslices) by splitting at each "TICK" instruction. For
        each circuit layer the number of qubits acted upon is found, and any qubits that
        are not involved in the layer have idle noise applied to them at the end of the
        timeslice.

        Total qubit count is found by looking for qubit definitions - QUBIT_COORDS
        entries in the full circuit.

        Returns
        -------
        stim.Circuit
            New stim circuit with idle noise.

        Raises
        ------
        ValueError
            If the circuit does not have qubit coordinate definitions.
        """
        qubit_indices = set(
            next(x.value for x in line.targets_copy())
            for line in circuit
            if line.name == StimDecorators.QUBIT_COORDS
        )
        if not qubit_indices:
            raise ValueError(
                "You must define qubit entries for idle noise to be applied, "
                "otherwise stim has no way of knowing how many qubits are involved "
                "in the experiment. Add QUBIT_COORDS commands to the beginning of the"
                " circuit."
            )
        circuit_layers = get_circuit_layers(circuit=circuit)
        final_circuit = stim.Circuit()
        for timeslice in circuit_layers:
            if len(timeslice) == 0:
                continue
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
        if self._idle_noise_parameter:
            return self.add_idle_noise(noisy_circuit)
        return noisy_circuit
