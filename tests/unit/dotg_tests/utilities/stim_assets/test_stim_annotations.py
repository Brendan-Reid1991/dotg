from dotg.utilities.stim_assets import StimAnnotations

from .base_test_stim_operations import BaseTestStimOperations

CURRENT_ANNOTATIONS = [
    "DETECTOR",
    "OBSERVABLE_INCLUDE",
    "QUBIT_COORDS",
    "TICK",
    "SHIFT_COORDS",
]


class TestStimAnnotations(BaseTestStimOperations):
    ENUM = StimAnnotations
    CURRENT_MEMBERS = CURRENT_ANNOTATIONS
