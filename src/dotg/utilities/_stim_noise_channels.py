"""This module provides helpful enums for access to stim noise channels."""
from dotg.utilities._stim_operations import StimOperations


class SingleQubitNoiseChannels(StimOperations):
    """An enum detailing all relevant single qubit stim noise channels. The values are 
    the strings present in stim circuits.

    Options are:
        DEPOLARIZE1 - Single qubit depolarizing channel\n
        PAULI_CHANNEL_1 - Biased single qubit depolarising channel\n
        X_ERROR - X-error channel\n
        Y_ERROR - Y-error channel\n
        Z_ERROR - Z-error channel
    """
    DEPOLARIZE1 = "DEPOLARIZE1"
    PAULI_CHANNEL_1 = "PAULI_CHANNEL_1"
    X_ERROR = "X_ERROR"
    Y_ERROR = "Y_ERROR"
    Z_ERROR = "Z_ERROR"


class TwoQubitNoiseChannels(StimOperations):
    """An enum detailing all relevant two qubit stim noise channels. The values are 
    the strings present in stim circuits.

    Options are:
        DEPOLARIZE2 - Two qubit depolarizing channel\n
        PAULI_CHANNEL_2 - Biased two qubit depolarising channel
    """
    DEPOLARIZE2 = "DEPOLARIZE2"
    PAULI_CHANNEL_2 = "PAULI_CHANNEL_2"
