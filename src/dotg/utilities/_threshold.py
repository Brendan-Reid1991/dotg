"""This module provides a class for detecting the threshold of an experiment."""
from typing import Callable, Dict, List, Tuple
from warnings import warn

import numpy as np
from numpy.typing import NDArray
from scipy.interpolate import interp1d
from scipy.optimize import newton


class ThresholdHeuristic:
    """This class implements a heuristic method for distilling an approximate value of
    the threshold, given a dictionary of logical error curves indexed by their distances.

    This is done by first interpolating the logical error curves along a more fine-
    grained physical error array, then taking the difference of sequential distance
    values and approximating the zero root via Newton Raphson. The approximate threshold
    is reported as the median of these values. The lowest value distance is excluded in
    an attempt to avoid finite size effects.

    Parameters
    ----------
    physical_errors : NDArray | List[float]
        Physical error parameters used in the experiment.
    logical_errors_by_distance : Dict[int, NDArray  |  List[float]]
        Dictionary of logical error curves indexed by their code distances.
    log_scale : bool, optional
        Whether or not the physical errors are in logscale, by default True.
    """

    def __init__(
        self,
        physical_errors: NDArray | List[float],
        logical_errors_by_distance: Dict[int, NDArray | List[float]],
        log_scale: bool = True,
    ):
        self.physical_errors = physical_errors
        self.logical_errors_by_distance = logical_errors_by_distance
        self.log_scale = log_scale
        self._num_points = int(1e4)

        if self.log_scale:
            self.fine_grained_physical_errors = np.logspace(
                np.log10(self.physical_errors[0]),
                np.log10(self.physical_errors[-1]),
                self._num_points,
            )
        else:
            warn(
                "Unsure of the behaviour without a log scale x-axis. Needs investigated."
            )
            self.fine_grained_physical_errors = np.linspace(
                self.physical_errors[0], self.physical_errors[-1], self._num_points
            )

    def get_fitting_function(self, logical_errors: List[float] | NDArray) -> Callable:
        """Get the interpolation function for the given curve.

        Parameters
        ----------
        logical_errors : List[float] | NDArray
            List of logical error values.

        Returns
        -------
        Callable
            Callable function for interpolation.
        """
        return interp1d(self.physical_errors, logical_errors)

    def logical_errors_interpolated(self) -> Dict[int, NDArray]:
        """Get the interpolated version of the input logical error dictionary.

        Returns
        -------
        Dict[int, NDArray]
            Dictionary of interpolated logical error curves indexed by their code
            distances.
        """
        return {
            distance: self.get_fitting_function(logical_error)(
                self.fine_grained_physical_errors
            )
            for distance, logical_error in self.logical_errors_by_distance.items()
        }

    def _approximate_crossover(
        self, interpolated_curve_1: NDArray, interpolated_curve_2: NDArray
    ) -> float:
        """Approximate the crossover point of two interpolated curves, by interpolating
        their difference and finding the root via the Newton Raphson method. Root finding
        starts at 3/4 of the way along the physical error rates.

        Parameters
        ----------
        interpolated_curve_1 : NDArray
            First interpolated curve.
        interpolated_curve_2 : NDArray
            Second interpolated curve.

        Returns
        -------
        float
            Approximate x-axis value (physical error rate) where the curves are equal.
        """
        starting_point = 0.75 * self.fine_grained_physical_errors[-1]
        interpolated_difference = interp1d(
            self.fine_grained_physical_errors,
            interpolated_curve_2 - interpolated_curve_1,
        )
        return newton(interpolated_difference, starting_point)

    def threshold(self) -> Tuple[float, float]:
        """Approximate the value of the threshold by comparing sequential distance
        values, and reporting the median and standard deviation.

        Returns
        -------
        Tuple[float, float]
            Median and standard deviation of approximate thresholds.
        """
        logical_error_interpolated = self.logical_errors_interpolated()
        distances = list(logical_error_interpolated.keys())
        threshold_guess = [
            self._approximate_crossover(
                logical_error_interpolated[_d2], logical_error_interpolated[_d1]
            )
            for _d1, _d2 in zip(distances[1:-1], distances[2:])
        ]

        return np.median(threshold_guess), np.std(threshold_guess)  # type: ignore
