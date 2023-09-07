import pytest
import stim

from dotg.noise import NoiseModel
from dotg.utilities.stim_assets import OneQubitNoiseChannels, TwoQubitNoiseChannels


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
                "Invalid noise parameter passed for channel DEPOLARIZE2: 1",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, -0.5),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel DEPOLARIZE1: -0.5",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.Y_ERROR, -0.045),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel Y_ERROR: -0.045",
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
            match="stim noise channels `PAULI_CHANNEL_1` and"
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

    @pytest.mark.parametrize(
        "circuit, expected_output",
        [
            (
                stim.Circuit(
                    """R 0 1 2
                M 0 1 2
                """
                ),
                stim.Circuit(
                    """R 0 1 2
                Y_ERROR(0.001) 0 1 2
                M(0.01) 0 1 2
                """
                ),
            ),
            (
                stim.Circuit(
                    """R 0 1 2
                H 0 1
                CX 1 2
                M 0 1 2"""
                ),
                stim.Circuit(
                    """R 0 1 2
                Y_ERROR(0.001) 0 1 2
                H 0 1
                DEPOLARIZE1(0.01) 0 1
                CX 1 2
                DEPOLARIZE2(0.01) 1 2
                M(0.01) 0 1 2"""
                ),
            ),
            (
                stim.Circuit(
                    """R 0 1 2 3 4
                H 0 1 2
                MR 0 1 2 3 4"""
                ),
                stim.Circuit(
                    """R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                H 0 1 2
                DEPOLARIZE1(0.01) 0 1 2
                M(0.01) 0 1 2 3 4
                R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                """
                ),
            ),
            (
                stim.Circuit(
                    """R 0 1
                Y 0 1
                TICK"""
                ),
                stim.Circuit(
                    """R 0 1
                Y_ERROR(0.001) 0 1
                Y 0 1
                DEPOLARIZE1(0.01) 0 1
                TICK
                """
                ),
            ),
        ],
    )
    def test_output_from_permute_circuit(self, noise_model, circuit, expected_output):
        assert expected_output == noise_model.permute_circuit(circuit)
