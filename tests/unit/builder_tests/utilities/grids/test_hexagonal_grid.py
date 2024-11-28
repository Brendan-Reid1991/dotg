from builder.utilities.grids import HexagonalGrid
import pytest


class TestHexagonalGrid:

    def test_Displacer_values(self):
        check_displacer = lambda displacement, expected: (
            displacement.value == expected,
            f"{displacement.name} value should be {(0.5, 1)}. Received {displacement.value}",
        )
        expected_values = [(0.5, 1), (1, 0), (0.5, -1), (-0.5, -1), (-1, 0), (-0.5, 1)]
        for displacement, expected in zip(HexagonalGrid.Displacer, expected_values):
            is_equal, msg = check_displacer(displacement, expected)
            assert is_equal, msg

    @pytest.mark.parametrize("x_lim, y_lim", [(0, 0), (1, 3), (4, 5), (10, 11)])
    def test_error_raised_for_invalid_dimensions(self, x_lim, y_lim):
        with pytest.raises(ValueError, match=r"Invalid dimensions for hexagonal grid."):
            HexagonalGrid(x_lim=x_lim, y_lim=y_lim)


    def test_schedules(self)