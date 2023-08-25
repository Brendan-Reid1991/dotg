import pytest

from tests.unit.circuits import NOISELESS_CIRCUIT

class BasicDecoderTests:
    DECODER_CLASS: 
    def test_raises_NoNoiseError_for_no_noise(self):
        assert 