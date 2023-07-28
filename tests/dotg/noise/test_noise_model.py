import pytest

from dotg.noise import NoiseModel
from dotg.utilities import TwoQubitNoiseChannels, OneQubitNoiseChannels


class TestNoiseModel:
    @pytest.fixture(scope="class")
    def noise_model(self):
        return NoiseModel(
            two_qubit_gate_noise=(TwoQubitNoiseChannels.DEPOLARIZE2, 0.01),
            one_qubit_gate_noise=(OneQubitNoiseChannels.DEPOLARIZE1, 0.01),
            reset_noise=(OneQubitNoiseChannels.Y_ERROR, 0.001),
            measurement_noise=1e-2,
        )

    @pytest.mark.parametrize(
        "noise_channels, expected_error_msg",
        [
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.01),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel "
                "TwoQubitNoiseChannels.DEPOLARIZE2: 1",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, -0.5),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel "
                "OneQubitNoiseChannels.DEPOLARIZE1: -0.5",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.Y_ERROR, 0.0),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel "
                "OneQubitNoiseChannels.Y_ERROR: 0.0",
            ],
        ],
    )
    def test_error_raised_if_invalid_noise_param(
        self, noise_channels, expected_error_msg
    ):
        with pytest.raises(ValueError, match=expected_error_msg):
            NoiseModel(*noise_channels)

    @pytest.mark.parametrize(
        "noise_channels",
        [
            (OneQubitNoiseChannels.PAULI_CHANNEL_1, (0.01, 0.02)),
            (OneQubitNoiseChannels.PAULI_CHANNEL_1, 0.001),
            (TwoQubitNoiseChannels.PAULI_CHANNEL_2, 0.01),
            (TwoQubitNoiseChannels.PAULI_CHANNEL_2, (0.01, 0.02)),
        ],
    )
    def test_pauli_channel_raises_error_if_tuples_of_incorrect_length_passed(
        self, noise_channels
    ):
        with pytest.raises(
            ValueError,
            match="Stim noise channels `PAULI_CHANNEL_1` and"
            " `PAULI_CHANNEL_2` must be accompanied with tuple of floats "
            "of lengths 3 and 15 respectively.",
        ):
            if noise_channels[0] is TwoQubitNoiseChannels.PAULI_CHANNEL_2:
                NoiseModel(
                    two_qubit_gate_noise=noise_channels,
                    one_qubit_gate_noise=(OneQubitNoiseChannels.DEPOLARIZE1, 0.01),
                    reset_noise=(OneQubitNoiseChannels.Y_ERROR, 0.001),
                    measurement_noise=1e-2,
                )
            else:
                NoiseModel(
                    two_qubit_gate_noise=(TwoQubitNoiseChannels.DEPOLARIZE2, 0.01),
                    one_qubit_gate_noise=noise_channels,
                    reset_noise=(OneQubitNoiseChannels.Y_ERROR, 0.001),
                    measurement_noise=1e-2,
                )

    def test_value_error_raised_for_incorrect_msmt_flip(self):
        with pytest.raises(ValueError, match=r"Invalid measurement flip value given:*"):
            NoiseModel(
                two_qubit_gate_noise=(TwoQubitNoiseChannels.DEPOLARIZE2, 0.01),
                one_qubit_gate_noise=(OneQubitNoiseChannels.DEPOLARIZE1, 0.01),
                reset_noise=(OneQubitNoiseChannels.Y_ERROR, 0.001),
                measurement_noise=2,
            )