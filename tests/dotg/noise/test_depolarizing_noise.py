import pytest
import stim

from dotg.noise import DepolarizingNoise


class TestDepolarizingNoise:
    @pytest.fixture(scope="class")
    def noise_model(self):
        return DepolarizingNoise(physical_error=1e-3)

    @pytest.mark.parametrize("invalid_param", (-1, 0, 1, 2, 4.1))
    def test_value_error_raised_for_invalid_param(self, invalid_param):
        with pytest.raises(
            ValueError, match="Physical error probability must be between 0 and 1"
        ):
            DepolarizingNoise(invalid_param)

    @pytest.mark.parametrize("param", (0.01, 0.001111, 0.53322, 0.04445134))
    def test_correct_param_is_returned(self, param):
        assert DepolarizingNoise(param).physical_error == param

    @pytest.mark.parametrize(
        "input_param, replacement_param", ((0.01, 0.001111), (0.53322, 0.04445134))
    )
    def test_physical_error_setter_replaces_value(self, input_param, replacement_param):
        depolarize = DepolarizingNoise(input_param)
        depolarize.physical_error = replacement_param
        assert depolarize.physical_error == replacement_param
