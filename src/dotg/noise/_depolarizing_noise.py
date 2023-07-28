"""This module defines depolarizing noise models."""

from dotg.noise._noise_model import NoiseModel
from dotg.utilities import TwoQubitNoiseChannels, OneQubitNoiseChannels

# pylint: disable=super-init-not-called


class DepolarizingNoise(NoiseModel):
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
        If physical_error does not lie in the range (0, 1).
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
        super().__init__(
            two_qubit_gate_noise=(
                TwoQubitNoiseChannels.DEPOLARIZE2,
                self._physical_error,
            ),
            one_qubit_gate_noise=(
                OneQubitNoiseChannels.DEPOLARIZE1,
                self._physical_error / 10,
            ),
            reset_noise=(OneQubitNoiseChannels.DEPOLARIZE1, self._physical_error / 10),
            measurement_noise=self._physical_error,
        )
