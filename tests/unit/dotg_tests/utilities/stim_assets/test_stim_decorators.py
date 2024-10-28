from dotg.utilities.stim_assets import StimAnnotations

from .base_test_stim_operations import BaseTestStimOperations

CURRENT_DECORATORS = [
    "DETECTOR",
    "OBSERVABLE_INCLUDE",
    "QUBIT_COORDS",
    "TICK",
]


class TestStimDecorators(BaseTestStimOperations):
    ENUM = StimAnnotations
    CURRENT_MEMBERS = CURRENT_DECORATORS
