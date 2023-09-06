import pytest

from dotg.decoders import BPOSD
from dotg.decoders._belief_propagation_base_class import (LDPC_DecoderOptions,
                                                          MessageUpdates,
                                                          OSDMethods)
from tests.unit.decoders._basic_tests._basic_bp_bposd_tests import (
    BasicBeliefPropagationDecoderTests, BasicCircuits)
from tests.unit.decoders._basic_tests._basic_decoder_tests import \
    BasicDecoderTests


@pytest.mark.xfail(reason="Haven't gotten around to this one yet.")
class TestBPOSD(BasicBeliefPropagationDecoderTests, BasicDecoderTests):
    DECODER_CLASS = BPOSD
