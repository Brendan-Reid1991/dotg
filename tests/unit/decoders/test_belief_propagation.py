import pytest

from dotg.decoders import BeliefPropagation
from tests.unit.circuits._basic_circuits import BasicCircuits
from tests.unit.decoders._basic_decoder_tests import BasicDecoderTests


class TestBeliefPropagatin(BasicDecoderTests):
    DECODER_CLASS = BeliefPropagation

    def test_raises_NoNoiseError_for_no_noise(self):
        return super().test_raises_NoNoiseError_for_no_noise(
            max_iterations=1, message_updates=0
        )
