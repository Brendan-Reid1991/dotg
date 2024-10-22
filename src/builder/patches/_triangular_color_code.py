"""Defines physical qubits on the triangular color code."""

import matplotlib

from builder.utilities import QubitCoordinate
from builder.patches.grids import HexagonalGrid
from builder.utilities import Visualiser


def _num_data_qubits_in_triangular_color_code(distance: int) -> int:
    """Formula for calculating the number of data qubits in a
    triangular color code of a set distance.

    Parameters
    ----------
    distance : int
        Integer value for the code distance.

    Returns
    -------
    int
        Total number of data qubits.
    """
    return sum(sorted(list(range(1, distance + 1)) + list(range(1, distance, 2))))


class TriangularColorCode:
    def __init__(
        self,
        code_distance: int,
        qubit_grid: HexagonalGrid,
        anchor: QubitCoordinate,
    ) -> None:
        self.code_distance = code_distance
        if self.code_distance % 2 == 0:
            raise ValueError(
                "Code distance must be an odd integer, received d=", self.code_distance
            )
        self.qubit_grid = qubit_grid
        self.anchor = (
            anchor if isinstance(anchor, QubitCoordinate) else QubitCoordinate(*anchor)
        )
        if self.anchor not in self.qubit_grid.data_qubits:
            raise ValueError(
                f"""Invalid anchor: {self.anchor}. 
                The anchor designates the bottom left hand corner data qubit; 
                chosen anchor is not a data qubit. 
                All data qubit coordinates can be accessed through the {self.qubit_grid.__class__.__name__} method 'data_qubits'."""
            )

        def in_code(qubit: QubitCoordinate) -> bool:
            displaced: QubitCoordinate = QubitCoordinate(
                qubit.x - self.anchor.x, qubit.y - self.anchor.y
            )
            not_in_negative_space: bool = displaced.x >= 0 and displaced.y >= 0
            within_the_outer_boundaries: bool = (
                max(0, displaced.y / 2)
                <= displaced.x
                < ((self.code_distance + self.code_distance // 2) - (displaced.y / 2))
            )
            return within_the_outer_boundaries

        self.data_qubits: list[QubitCoordinate] = list(
            filter(in_code, self.qubit_grid.data_qubits)
        )
        if len(self.data_qubits) != _num_data_qubits_in_triangular_color_code(
            distance=self.code_distance
        ):
            raise ValueError(
                f"""Invalid number of data qubits! 
                It's possible that your grid size is too small.
                For code distance {self.code_distance} you require a grid of dimension
                {(self.code_distance+self.code_distance // 2, self.code_distance+self.code_distance // 2)} at least. Your anchor qubit could also
                be placing the logical qubit too close to the grid edges. 
                """
            )
        self.red_qubits: list[QubitCoordinate] = list(
            filter(in_code, self.qubit_grid.red_qubits)
        )
        self.blue_qubits: list[QubitCoordinate] = list(
            filter(in_code, self.qubit_grid.blue_qubits)
        )
        self.green_qubits: list[QubitCoordinate] = list(
            filter(in_code, self.qubit_grid.green_qubits)
        )

    def __str__(self):
        return f"""TriangularColorCode(d={self.code_distance}) @ {self.anchor} on 
        {self.qubit_grid.__class__.__name__}({self.qubit_grid._x_lim, self.qubit_grid._y_lim})"""

    def draw(
        self,
        figsize: tuple[int, int] = (10, 8),
        indices: bool = True,
    ) -> matplotlib.figure.Figure:
        """Draw the patch on the grid, colouring in the stabilizers and optionally adding the indices.

        Parameters
        ----------
        figsize: tuple[int, int], optional
            The figure size, by default (10, 8).
        indices : bool, optional
            Add index labels to the qubits, by default True

        Returns
        -------
        matplotlib.figure.Figure
            A matplotlib Figure object.
        """
        vis = Visualiser(grid=self.qubit_grid, figsize=figsize, show_indices=indices)
        for color, qubits in {
            "red": self.red_qubits,
            "blue": self.blue_qubits,
            "green": self.green_qubits,
        }.items():
            for qubit in qubits:
                vis.draw_stabilizer(
                    stabilizer=qubit,
                    color=color,
                    data_qubit_member_check=self.data_qubits,
                )
        for dq in self.data_qubits:
            vis.draw_qubit(qubit=dq)

        return vis.figure
