from typing import Type

import pytest

from dotg.decoders._decoder_base_classes._decoder_base_class import Decoder
from dotg.utilities._syndrome_sampler import NoNoiseInCircuitError
from tests.unit.circuits import BasicMemoryCircuits


class BasicDecoderTests:
    DECODER_CLASS: Type[Decoder]

    def test_raises_NoNoiseError_for_no_noise(self, *args, **kwargs):
        with pytest.raises(
            NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]
        ):
            self.DECODER_CLASS(
                BasicMemoryCircuits.GraphLike.NOISELESS_CIRCUIT, *args, **kwargs
            )
        with pytest.raises(
            NoNoiseInCircuitError, match=NoNoiseInCircuitError().args[0]
        ):
            self.DECODER_CLASS(
                BasicMemoryCircuits.HypergraphLike.NOISELESS_CIRCUIT, *args, **kwargs
            )
