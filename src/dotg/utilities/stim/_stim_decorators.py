"""This module provides helpful enums for access to stim decorators."""
from dotg.utilities.stim._stim_operations import StimOperations


class StimDecorators(StimOperations):
    """An enum detailing all relevant stim decorators. The values are the strings that
    are present in stim circuits.

    Options are:
        DETECTOR - Dectector annotation\n
        OBSERVABLE_INCLUDE - Logical observable annotation\n
        QUBIT_COORDS - Qubit coordinates annotation\n
        TICK - Circuit layer annotation
    """

    DETECTOR = "DETECTOR"
    OBSERVABLE_INCLUDE = "OBSERVABLE_INCLUDE"
    QUBIT_COORDS = "QUBIT_COORDS"
    TICK = "TICK"
