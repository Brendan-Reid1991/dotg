from dotg.utilities.stim_assets import (
    MeasureAndReset,
    MeasurementGates,
    OneQubitGates,
    ResetGates,
    TwoQubitGates,
)

from .base_test_stim_operations import BaseTestStimOperations

CURRENT_ONE_QUBIT_GATES = [
    "I",
    "X",
    "Y",
    "Z",
    "H",
    "S",
    "S_DAG",
    "SQRT_X",
    "SQRT_X_DAG",
    "SQRT_Y",
    "SQRT_Y_DAG",
    "SQRT_Z",
    "SQRT_Z_DAG",
]
CURRENT_TWO_QUBIT_GATES = ["CX", "CY", "CZ", "SQRT_XX"]
CURRENT_RESET_GATES = ["R", "RX", "RZ", "RY"]
CURRENT_MEASUREMENT_GATES = ["M", "MX", "MZ", "MY"]
CURRENT_MEASUREMENT_AND_RESET_GATES = ["MR"]


class TestOneQubitGates(BaseTestStimOperations):
    ENUM = OneQubitGates
    CURRENT_MEMBERS = CURRENT_ONE_QUBIT_GATES


class TestTwoQubitGates(BaseTestStimOperations):
    ENUM = TwoQubitGates
    CURRENT_MEMBERS = CURRENT_TWO_QUBIT_GATES


class TestResetGates(BaseTestStimOperations):
    ENUM = ResetGates
    CURRENT_MEMBERS = CURRENT_RESET_GATES


class TestMeasureAndReset(BaseTestStimOperations):
    ENUM = MeasureAndReset
    CURRENT_MEMBERS = CURRENT_MEASUREMENT_AND_RESET_GATES


class TestMeasurementGates(BaseTestStimOperations):
    ENUM = MeasurementGates
    CURRENT_MEMBERS = CURRENT_MEASUREMENT_GATES
