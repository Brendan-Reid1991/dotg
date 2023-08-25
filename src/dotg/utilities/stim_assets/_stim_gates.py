"""This module provides helpful enums for access to stim gates."""
from dotg.utilities.stim_assets._stim_operations import StimOperations


class OneQubitGates(StimOperations):
    """An enum detailing all relevant single qubit stim gates. The values are the strings
    present in stim circuits.

    Options are:
        I - Identity gate\n
        X - Pauli-X gate\n
        Y - Pauli-Y gate\n
        Z - Pauli-Z gate\n
        H - Hadamard gate\n
        S - S gate\n
        S_DAG - Inverse S gate\n
        SQRT_{X, Y, Z} - SQRT_{X, Y, Z} gate\n
        SQRT_{X, Y, Z}_DAG - SQRT_{X, Y, Z}_DAG gate\n
    """

    I = "I"
    X = "X"
    Y = "Y"
    Z = "Z"
    H = "H"
    S = "S"
    S_DAG = "S_DAG"
    SQRT_X = "SQRT_X"
    SQRT_X_DAG = "SQRT_X_DAG"
    SQRT_Y = "SQRT_Y"
    SQRT_Y_DAG = "SQRT_Y_DAG"
    SQRT_Z = "SQRT_Z"
    SQRT_Z_DAG = "SQRT_Z_DAG"


class TwoQubitGates(StimOperations):
    """An enum detailing all relevant two qubit stim gates. The values are the strings
    present in stim circuits.

    Options are:
        CX - Controlled-X gate\n
        CNOT - Alterantive to CX\n
        CY - Controlled-Y gate\n
        CZ - Controlled-Z gate\n
        SQRT_XX - Two qubit XX rotation. More commonly known as Molmer -orensen interaction.
    """

    CX = "CX"
    CNOT = "CX"
    CY = "CY"
    CZ = "CZ"
    SQRT_XX = "SQRT_XX"


class ResetGates(StimOperations):
    """An enum detailing all relevant reset stim gates. The values are the strings
    present in stim circuits.

    Options are:
        R - Z-basis reset\n
        RX - X-basis reset\n
        RY - Y-basis reset\n
        RZ - Z-basis reset
    """

    R = "R"
    RX = "RX"
    RZ = "RZ"
    RY = "RY"


class MeasurementGates(StimOperations):
    """An enum detailing all relevant measurment stim gates. The values are the strings
    present in stim circuits.

    Options are:
        M - Z-basis measurement\n
        MX - X-basis measurement\n
        MY - Y-basis measurement\n
        MZ - Z-basis measurement\n

    """

    M = "M"
    MX = "MX"
    MZ = "MZ"
    MY = "MY"


class MeasureAndReset(StimOperations):
    """Unique enum to capture the MR stim instruction.

    Options are:
        MR - measurement and reset command.
    """

    MR = "MR"
