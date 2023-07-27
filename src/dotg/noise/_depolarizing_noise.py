"""This module defines depolarizing noise models."""

import stim
from dotg.utilities import (
    SingleQubitNoiseChannels,
    TwoQubitNoiseChannels,
    StimDecorators,
    SingleQubitGates,
    TwoQubitGates,
    ResetGates,
    MeasurementGates,
    MeasureAndReset,
)


class DepolarizingNoise:
    """Class that allows application of depolarizing noise onto a noiseless stim circuit.
    It takes in a single parameter, physical_error, which acts as the two qubit gate
    noise and the measurement noise. All other noise parameters (single quibt gates
    and reset gates) take the value physical_error*0.1.

    Parameters
    ----------
    physical_error : float
        Probability of a physical error occurring at any one location in the
        quantum circuit.

    Raises
    ------
    ValueError
        If physical_error is not between 0 and 1, exclusive.

    Methods
    -------
    permute_circuit(circuit: stim.Circuit) -> stim.Circuit
        This method takes as input a stim circuit without noise, and applies
        noise channels after each operation in the circuit.
    """

    def __init__(self, physical_error: float) -> None:
        self._physical_error = physical_error
        self.physical_error = self._physical_error
        if not 0 < self._physical_error < 1:
            raise ValueError("Physical error probability must be between 0 and 1.")

    @property
    def physical_error(self) -> float:
        """Return the physical error parameter.

        Returns
        -------
        float
        """
        return self._physical_error

    @physical_error.setter
    def physical_error(self, new_value):
        self._physical_error = new_value
        self._single_qubit_gate_noise = self._physical_error / 10
        self._reset_noise = self._physical_error / 10
        self._two_qubit_gate_noise = self._physical_error
        self._measurement_noise = self._physical_error

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
                    arg=self._measurement_noise,
                )
                noisy_circuit.append(
                    name=ResetGates.RZ.value, targets=instr.targets_copy()
                )
                noisy_circuit.append(
                    name=SingleQubitNoiseChannels.DEPOLARIZE1.value,
                    targets=instr.targets_copy(),
                    arg=self._reset_noise,
                )
                continue

            if instr.name in MeasurementGates.members():
                noisy_circuit.append(
                    name=instr.name,
                    targets=instr.targets_copy(),
                    arg=self._measurement_noise,
                )
                continue

            noisy_circuit.append(instr)
            if instr.name in StimDecorators.members():
                continue

            if instr.name in SingleQubitGates.members() + ResetGates.members():
                noisy_circuit.append(
                    name=SingleQubitNoiseChannels.DEPOLARIZE1.value,
                    targets=instr.targets_copy(),
                    arg=self._single_qubit_gate_noise,
                )

            if instr.name in TwoQubitGates.members():
                noisy_circuit.append(
                    name=TwoQubitNoiseChannels.DEPOLARIZE2.value,
                    targets=instr.targets_copy(),
                    arg=self._two_qubit_gate_noise,
                )

        return noisy_circuit
