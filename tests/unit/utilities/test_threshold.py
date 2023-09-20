from ast import literal_eval

import numpy as np
import pytest

from dotg.utilities import ThresholdHeuristic


class TestThreshold:
    PHYSICAL_ERRORS = np.logspace(-3, -2, 20)
    with open(
        "tests/unit/utilities/threshold_test_data/logical_error_test_data_x.txt",
        "r",
        encoding="utf-8",
    ) as _data:
        X_MEMORY_LOGICAL = literal_eval(_data.read())
    with open(
        "tests/unit/utilities/threshold_test_data/logical_error_test_data_z.txt",
        "r",
        encoding="utf-8",
    ) as _data:
        Z_MEMORY_LOGICAL = literal_eval(_data.read())

    @pytest.fixture(scope="class")
    def ThresholdX(self):
        return ThresholdHeuristic(
            physical_errors=self.PHYSICAL_ERRORS,
            logical_errors_by_distance=self.X_MEMORY_LOGICAL,
        )

    @pytest.fixture(scope="class")
    def ThresholdZ(self):
        return ThresholdHeuristic(
            physical_errors=self.PHYSICAL_ERRORS,
            logical_errors_by_distance=self.Z_MEMORY_LOGICAL,
        )

    def test_warning_raised_if_input_not_in_log_scale(self):
        with pytest.warns(
            match="Unsure of the behaviour without a log scale x-axis. Needs investigated."
        ):
            ThresholdHeuristic(
                physical_errors=self.PHYSICAL_ERRORS,
                logical_errors_by_distance=self.X_MEMORY_LOGICAL,
                log_scale=False,
            )

    @pytest.mark.parametrize("distances", ([3], [3, 5], [3, 5, 7]))
    def test_error_raised_if_not_enough_logical_curves(self, distances):
        with pytest.raises(
            ValueError,
            match="""While it is possible to distill a threshold on a small number of 
                logical curves, it is also not satisfying. Provide four or more curves 
                for high confidence in the approximation.""",
        ):
            logical_errors_by_distance_reduced = {
                dist: self.X_MEMORY_LOGICAL[dist] for dist in distances
            }
            ThresholdHeuristic(
                physical_errors=self.PHYSICAL_ERRORS,
                logical_errors_by_distance=logical_errors_by_distance_reduced,
                log_scale=True,
            )

    @pytest.mark.parametrize("thresholder", ["ThresholdX", "ThresholdZ"])
    def test_length_of_fine_grained_physical(self, thresholder, request):
        thresholder = request.getfixturevalue(thresholder)
        assert len(thresholder.fine_grained_physical_errors) == int(1e4)

    @pytest.mark.parametrize("thresholder", ["ThresholdX", "ThresholdZ"])
    def test_fitting_function_is_callable(self, thresholder, request):
        thresholder = request.getfixturevalue(thresholder)
        logical_errors = self.X_MEMORY_LOGICAL[3]
        assert callable(thresholder.get_fitting_function(logical_errors))

    @pytest.mark.parametrize(
        "thresholder, input_data",
        [("ThresholdX", X_MEMORY_LOGICAL), ("ThresholdZ", Z_MEMORY_LOGICAL)],
    )
    def test_logical_errors_interpolated_return_type(
        self, thresholder, input_data, request
    ):
        thresholder = request.getfixturevalue(thresholder)
        log_err_int = thresholder.logical_errors_interpolated()
        assert isinstance(
            log_err_int, dict
        ), f"Return type from logical_errors_interpolated should be dict, got {type(log_err_int)}"
        assert (
            log_err_int.keys() == input_data.keys()
        ), "Interpolated dictionaries do not have the same keys as input dictionaries."
        assert all(
            len(x) == 1e4 for x in log_err_int.values()
        ), f"Interpolated dictionaries do not have the correct length. Should be {int(1e4)} but got {[(dist, len(entry)) for dist, entry in log_err_int.items()]}"

    @pytest.mark.parametrize("thresholder", ["ThresholdX", "ThresholdZ"])
    def test_approximate_crossover_return_type(self, thresholder, request):
        thresholder = request.getfixturevalue(thresholder)
        curves = thresholder.logical_errors_interpolated()

        crossover = thresholder._approximate_crossover(curves[5], curves[7])
        assert isinstance(
            crossover, float
        ), f"Return type should be float, got {type(crossover)}."
        assert (
            0.007 <= crossover < 0.01
        ), f"For this dataset, crossover should be between .7% and 1%. Got {crossover}"

    @pytest.mark.parametrize(
        "thresholder, expected_threshold, expected_std",
        [
            ("ThresholdX", 0.008585413676753428, 0.0003796495922193518),
            ("ThresholdZ", 0.008677323470052975, 0.0003842135040109315),
        ],
    )
    def test_threshold_value(
        self, thresholder, request, expected_threshold, expected_std
    ):
        thresholder = request.getfixturevalue(thresholder)
        thres, std = thresholder.threshold()
        assert thres == pytest.approx(
            expected_threshold
        ), f"Threshold value was off. Should be {expected_threshold}, got {thres}."

        assert std == pytest.approx(
            expected_std
        ), f"Threshold standard deviation value was off. Should be {expected_std}, got {std}."
