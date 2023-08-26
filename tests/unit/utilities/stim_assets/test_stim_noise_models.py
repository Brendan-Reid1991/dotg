from dotg.utilities.stim_assets import (OneQubitNoiseChannels,
                                        TwoQubitNoiseChannels)

from .base_test_stim_operations import BaseTestStimOperations

CURRENT_ONE_QUBIT_NOISE_CHANNELS = [
    "DEPOLARIZE1",
    "PAULI_CHANNEL_1",
    "X_ERROR",
    "Y_ERROR",
    "Z_ERROR",
]

CURRENT_TWO_QUBIT_NOISE_CHANNELS = ["DEPOLARIZE2", "PAULI_CHANNEL_2"]


class TestOneQubitNoiseChannels(BaseTestStimOperations):
    ENUM = OneQubitNoiseChannels
    CURRENT_MEMBERS = CURRENT_ONE_QUBIT_NOISE_CHANNELS


class TestTwoQubitNoiseChannels(BaseTestStimOperations):
    ENUM = TwoQubitNoiseChannels
    CURRENT_MEMBERS = CURRENT_TWO_QUBIT_NOISE_CHANNELS
