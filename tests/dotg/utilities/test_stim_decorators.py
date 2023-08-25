from dotg.utilities import StimDecorators

from .base_test_stim_operations import BaseTestStimOperations

CURRENT_DECORATORS = [
    "DETECTOR",
    "OBSERVABLE_INCLUDE",
    "QUBIT_COORDS",
    "TICK",
]


class TestStimDecorators(BaseTestStimOperations):
    ENUM = StimDecorators
    CURRENT_MEMBERS = CURRENT_DECORATORS
