from enum import Enum


class SingleQubitGates(Enum):
    """An enum detailing all relevant single qubit stim gates. The values are the strings
    present in stim circuits.

    Options are:
        I - Identity gate
        X - Pauli-X gate
        Y - Pauli-Y gate
        Z - Pauli-Z gate
        H - Hadamard gate
        S - S gate
        S_DAG - Inverse S gate
        SQRT_{X, Y, Z} - SQRT_{X, Y, Z} gate
        SQRT_{X, Y, Z}_DAG - SQRT_{X, Y, Z}_DAG gate
    """
    I = "I"
    X = "X"
    Z = "Z"
    Y = "Y"
    H = "H"
    S = "S"
    S_DAG = "S_DAG"
    SQRT_X = "SQRT_X"
    SQRT_X_DAG = "SQRT_X_DAG"
    SQRT_Y = "SQRT_Y"
    SQRT_Y_DAG = "SQRT_Y_DAG"
    SQRT_Z = "SQRT_Z"
    SQRT_Z_DAG = "SQRT_Z_DAG"


class TwoQubitGates(Enum):
    """An enum detailing all relevant two qubit stim gates. The values are the strings
    present in stim circuits.

    Options are:
        CX - Controlled-X gate
        CNOT - Alterantive to CX
        CY - Controlled-Y gate
        CZ - Controlled-Z gate
        SQRT_XX - Two qubit XX rotation. More commonly known as Molmer Sorensen 
        interaction
    """
    CX = "CX"
    CNOT = "CX"
    CY = "CY"
    CZ = "CZ"
    SQRT_XX = "SQRT_XX"


class ResetGates(Enum):
    """An enum detailing all relevant reset stim gates. The values are the strings
    present in stim circuits.

    Options are:
        R - Z-basis reset
        RX - X-basis reset
        RY - Y-basis reset
        Rz - Z-basis reset
    """
    R = "R"
    RX = "RX"
    RZ = "RZ"
    RY = "RY"


class MeasurementGates(Enum):
    """An enum detailing all relevant measurment stim gates. The values are the strings 
    present in stim circuits.

    Options are:
        M - Z-basis measurement
        MX - X-basis measurement
        MY - Y-basis measurement
        MZ - Z-basis measurement

    """
    M = "M"
    MX = "MX"
    MZ = "MZ"
    MY = "MY"
