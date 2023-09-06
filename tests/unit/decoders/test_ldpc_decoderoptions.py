import pytest

from dotg.decoders._belief_propagation_base_class import (LDPC_DecoderOptions,
                                                          MessageUpdates,
                                                          OSDMethods)


def test_message_updates_int_enum():
    assert [x.name for x in MessageUpdates] == ["PROD_SUM", "MIN_SUM"]
    assert [x.value for x in MessageUpdates] == [0, 1]


def test_osd_methods_int_enum():
    assert [x.name for x in OSDMethods] == [
        "ZERO",
        "EXHAUSTIVE",
        "COMBINATION_SWEEP",
    ]
    assert [x.value for x in OSDMethods] == [0, 1, 2]


class TestLDPC_DecoderOptions:
    @pytest.mark.parametrize("max_iterations", (-1, 0, 0.325))
    def test_invalid_max_iterations_raises_value_error(self, max_iterations):
        with pytest.raises(
            ValueError, match="Max iterations needs to be a positive, non-zero integer."
        ):
            LDPC_DecoderOptions(max_iterations=max_iterations)

    @pytest.mark.parametrize("msg_updates", [-2, -1, 2, 3, 4, 5])
    def test_error_raised_for_invalid_message_updates(self, msg_updates):
        with pytest.raises(ValueError, match="Invalid message updating scheme."):
            LDPC_DecoderOptions(max_iterations=1, message_updates=msg_updates)

    def test_default_min_sum_scaling_factor(self):
        ldpc_do = LDPC_DecoderOptions(max_iterations=1, message_updates=1)
        assert ldpc_do.min_sum_scaling_factor == 1, (
            "Default min_sum scaling factor should be 1;"
            f" got {ldpc_do.min_sum_scaling_factor}"
        )

    @pytest.mark.parametrize("mssf", [range(10)])
    def test_setting_min_sum_scaling_factor(self, mssf):
        ldpc_do = LDPC_DecoderOptions(
            max_iterations=1, message_updates=1, min_sum_scaling_factor=mssf
        )
        assert ldpc_do.min_sum_scaling_factor == mssf

    @pytest.mark.parametrize("osd_method", [-2, -1, 3, 4, 5])
    def test_error_raised_for_invalid_osd_method(self, osd_method):
        with pytest.raises(ValueError, match="Invalid OSD method."):
            LDPC_DecoderOptions(max_iterations=1, osd_method=osd_method)

    @pytest.mark.parametrize("osd_order", [-2, -1, 3, 4, 5])
    def test_error_raised_for_providing_order_but_not_method(self, osd_order):
        with pytest.raises(ValueError, match="OSD Method configuration must be given."):
            LDPC_DecoderOptions(max_iterations=1, osd_order=osd_order)

    @pytest.mark.parametrize("osd_method, osd_order", [(0, 0), (1, 10), (2, -1)])
    def test_osd_method_changes_osd_order(self, osd_method, osd_order):
        ldpc_do = LDPC_DecoderOptions(max_iterations=1, osd_method=osd_method)
        assert ldpc_do.osd_method == osd_method and ldpc_do.osd_order == osd_order

    @pytest.mark.parametrize("osd_order", range(1, 10))
    def test_setting_osd_order_overwrites_default_value_for_osd_method_1(
        self, osd_order
    ):
        ldpc_do = LDPC_DecoderOptions(
            max_iterations=1, osd_method=OSDMethods.EXHAUSTIVE, osd_order=osd_order
        )
        assert ldpc_do.osd_order == osd_order
