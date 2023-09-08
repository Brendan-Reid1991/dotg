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
            idle_noise=(OneQubitNoiseChannels.Z_ERROR, 0.0025),
            measurement_noise=1e-2,
        )

    @pytest.fixture(scope="class")
    def noise_model_no_idle(self):
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
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel DEPOLARIZE2: 1",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, -0.5),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel DEPOLARIZE1: -0.5",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.Y_ERROR, -0.045),
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel Y_ERROR: -0.045",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.Y_ERROR, 0.045),
                    (OneQubitNoiseChannels.Z_ERROR, 1.025),
                    1e-2,
                ],
                "Invalid noise parameter passed for channel Z_ERROR: 1.025",
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
                TICK
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
    def test_output_from_permute_circuit_without_idle_noise(
        self, noise_model_no_idle, circuit, expected_output
    ):
        assert expected_output == noise_model_no_idle.permute_circuit(circuit)

    @pytest.mark.parametrize(
        "circuit, expected_output",
        [
            (
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                TICK
                M 0 1 2
                """
                ),
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                Y_ERROR(0.001) 0 1 2
                TICK
                M(0.01) 0 1 2
                """
                ),
            ),
            (
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                TICK
                H 0 1
                TICK
                CX 1 2
                TICK
                M 0 1 2"""
                ),
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                Y_ERROR(0.001) 0 1 2
                TICK
                H 0 1
                DEPOLARIZE1(0.01) 0 1
                Z_ERROR(0.0025) 2
                TICK
                CX 1 2
                DEPOLARIZE2(0.01) 1 2
                Z_ERROR(0.0025) 0
                TICK
                M(0.01) 0 1 2"""
                ),
            ),
            (
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                QUBIT_COORDS 3
                QUBIT_COORDS 4
                R 0 1 2 3 4
                TICK
                H 0 1 2
                TICK
                MR 0 1 2 3 4"""
                ),
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                QUBIT_COORDS 3
                QUBIT_COORDS 4
                R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                TICK
                H 0 1 2
                DEPOLARIZE1(0.01) 0 1 2
                Z_ERROR(0.0025) 3 4
                TICK
                M(0.01) 0 1 2 3 4
                TICK
                R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                """
                ),
            ),
        ],
    )
    def test_output_from_permute_circuit_with_idle_noise(
        self, noise_model, circuit, expected_output
    ):
        assert expected_output == noise_model.permute_circuit(circuit)

    @pytest.mark.parametrize(
        "noise_channels, expected_error_msg",
        [
            [
                [
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, -0.5),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                ],
                "Invalid gate/noise pairing: two_qubit_gate_noise - DEPOLARIZE1",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (TwoQubitNoiseChannels.PAULI_CHANNEL_2, 0.5),
                    (OneQubitNoiseChannels.Y_ERROR, 0.001),
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                ],
                "Invalid gate/noise pairing: one_qubit_gate_noise - PAULI_CHANNEL_2",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.045),
                    (OneQubitNoiseChannels.Z_ERROR, 0.025),
                ],
                "Invalid gate/noise pairing: reset_noise - DEPOLARIZE2",
            ],
            [
                [
                    (TwoQubitNoiseChannels.DEPOLARIZE2, 0.1),
                    (OneQubitNoiseChannels.DEPOLARIZE1, 0.1),
                    (OneQubitNoiseChannels.Y_ERROR, 0.045),
                    (TwoQubitNoiseChannels.PAULI_CHANNEL_2, 1.025),
                ],
                "Invalid gate/noise pairing: idle_noise - PAULI_CHANNEL_2",
            ],
        ],
    )
    def test_invalid_gate_noise_pairings_gives_value_error(
        self, noise_channels, expected_error_msg
    ):
        with pytest.raises(ValueError, match=expected_error_msg):
            NoiseModel(*noise_channels)

    @pytest.mark.parametrize(
        "noise_model, circuit, instruction, final_circuit",
        [
            (
                NoiseModel(measurement_noise=1e-2),
                stim.Circuit("""R 0 1 2"""),
                stim.CircuitInstruction(name="MZ", targets=[0, 1, 2], gate_args=[1e-2]),
                stim.Circuit(
                    """R 0 1 2
                M(0.01) 0 1 2
                """
                ),
            ),
            (
                NoiseModel(measurement_noise=1e-5),
                stim.Circuit(
                    """R 0 1 2 3 4
                H 0 1 2"""
                ),
                stim.CircuitInstruction(
                    name="MR", targets=[0, 1, 2, 3, 4], gate_args=[1e-5]
                ),
                stim.Circuit(
                    """R 0 1 2 3 4
                H 0 1 2
                M(0.00001) 0 1 2 3 4
                TICK
                R 0 1 2 3 4
                """
                ),
            ),
        ],
    )
    def test_measurement_instruction(
        self, noise_model, circuit, instruction, final_circuit
    ):
        assert final_circuit == noise_model._measurement_instruction(
            circuit, instruction
        )

    @pytest.mark.parametrize(
        "noise_model, circuit, instruction, final_circuit",
        [
            (
                NoiseModel(measurement_noise=1e-5),
                stim.Circuit(
                    """R 0 1 2 3 4
                H 0 1 2"""
                ),
                stim.CircuitInstruction(
                    name="MR", targets=[0, 1, 2, 3, 4], gate_args=[1e-5]
                ),
                stim.Circuit(
                    """R 0 1 2 3 4
                H 0 1 2
                M(0.00001) 0 1 2 3 4
                TICK
                R 0 1 2 3 4
                """
                ),
            )
        ],
    )
    def test_measurement_and_reset_instruction(
        self, noise_model, circuit, instruction, final_circuit
    ):
        assert final_circuit == noise_model._measurement_and_reset_instruction(
            circuit, instruction
        )

    @pytest.mark.parametrize(
        "noise_model, circuit, instruction, final_circuit",
        [
            (
                NoiseModel(
                    two_qubit_gate_noise=(TwoQubitNoiseChannels.DEPOLARIZE2, 0.01)
                ),
                stim.Circuit(
                    """
                CX 0 1 2 3"""
                ),
                stim.CircuitInstruction(name="CX", targets=[0, 1, 2, 3]),
                stim.Circuit(
                    """
                CX 0 1 2 3
                DEPOLARIZE2(0.01) 0 1 2 3
                """
                ),
            ),
            (
                NoiseModel(
                    one_qubit_gate_noise=(
                        OneQubitNoiseChannels.PAULI_CHANNEL_1,
                        (0.01, 0.002, 0.0003),
                    )
                ),
                stim.Circuit(
                    """
                H 0 1 2 3"""
                ),
                stim.CircuitInstruction(name="H", targets=[0, 1, 2, 3]),
                stim.Circuit(
                    """
                H 0 1 2 3
                PAULI_CHANNEL_1(0.01, 0.002, 0.0003) 0 1 2 3
                """
                ),
            ),
            (
                NoiseModel(reset_noise=(OneQubitNoiseChannels.Y_ERROR, 1e-5)),
                stim.Circuit(
                    """
                R 0 1 2 3"""
                ),
                stim.CircuitInstruction(name="R", targets=[0, 1, 2, 3]),
                stim.Circuit(
                    """
                R 0 1 2 3
                Y_ERROR(0.00001) 0 1 2 3
                """
                ),
            ),
        ],
    )
    def test_gate_instruction(self, noise_model, circuit, instruction, final_circuit):
        assert final_circuit == noise_model._gate_instruction(circuit, instruction)

    @pytest.mark.parametrize(
        "circuit, final_circuit",
        [
            (
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                QUBIT_COORDS 3
                QUBIT_COORDS 4
                R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                TICK
                H 0 1 2
                DEPOLARIZE1(0.01) 0 1 2
                TICK
                M(0.01) 2 3 4
                TICK
                R 2 3 4
                Y_ERROR(0.001) 2 3 4
                TICK
                """
                ),
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                QUBIT_COORDS 3
                QUBIT_COORDS 4
                R 0 1 2 3 4
                Y_ERROR(0.001) 0 1 2 3 4
                TICK
                H 0 1 2
                DEPOLARIZE1(0.01) 0 1 2
                Z_ERROR(0.0025) 3 4
                TICK
                M(0.01) 2 3 4
                Z_ERROR(0.0025) 0 1
                TICK
                R 2 3 4
                Y_ERROR(0.001) 2 3 4
                Z_ERROR(0.0025) 0 1
                TICK
                """
                ),
            ),
            (
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                Y_ERROR(0.001) 0 1 2
                TICK
                H 0 1
                DEPOLARIZE1(0.01) 0 1
                TICK
                CX 1 2
                DEPOLARIZE2(0.01) 1 2
                TICK
                M(0.01) 2
                TICK"""
                ),
                stim.Circuit(
                    """QUBIT_COORDS 0
                QUBIT_COORDS 1
                QUBIT_COORDS 2
                R 0 1 2
                Y_ERROR(0.001) 0 1 2
                TICK
                H 0 1
                DEPOLARIZE1(0.01) 0 1
                Z_ERROR(0.0025) 2
                TICK
                CX 1 2
                DEPOLARIZE2(0.01) 1 2
                Z_ERROR(0.0025) 0
                TICK
                M(0.01) 2
                Z_ERROR(0.0025) 0 1
                TICK"""
                ),
            ),
        ],
    )
    def test_apply_idle_noise(self, noise_model, circuit, final_circuit):
        assert final_circuit == noise_model.add_idle_noise(circuit)

    def test_circuits_without_defined_qubits_cannot_have_idle_noise_added(
        self, noise_model
    ):
        circuit = stim.Circuit(
            """R 0 1 2
                Y_ERROR(0.001) 0 1 2
                TICK
                H 0 1
                DEPOLARIZE1(0.01) 0 1
                TICK
                CX 1 2
                DEPOLARIZE2(0.01) 1 2
                TICK
                M(0.01) 2"""
        )

        with pytest.raises(
            ValueError,
            match="You must define qubit coordinates for idle noise to be applied, "
            "otherwise stim has no way of knowing how many qubits are involved "
            "in the experiment.",
        ):
            noise_model.permute_circuit(circuit)
