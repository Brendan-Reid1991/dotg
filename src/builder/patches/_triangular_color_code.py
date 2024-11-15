"""Defines physical qubits on the triangular color code."""

from __future__ import annotations
from typing import Optional
import matplotlib

from builder.patches._patch import Patch
from builder.utilities import QubitCoordinate
from builder.utilities.grids import HexagonalGrid

# mypy: disable-error-code=arg-type


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


class TriangularColorCode(Patch):
    """A patch class for defining a logical qubit on the triangular color code.

    Provide a single value as the code distance, the qubit grid to define the logical
    qubit on and the anchor qubit, which designates the bottom left hand corner data
    qubit.

    Only odd code distances are permitted.

    Parameters
    ----------
    distance: int
        The logical distance of the code.
    qubit_grid: HexagonalGrid
        The grid the logical qubit is placed on.
    anchor: QubitCoordinate
        The coordinate of the bottom left hand corner data qubit in the patch.

    Attributes
    ----------
    data_qubits: list[QubitCoordinate]
        A list of all the data qubits in the code.
    red_qubits: list[QubitCoordinate]
        A list of all red-colored plaquette qubits.
    blue_qubits: list[QubitCoordinate]
        A list of all blue-colored plaquette qubits.
    green_qubits: list[QubitCoordinate]
        A list of all green-colored plaquette qubits.

    Raises
    ------
    ValueError
        If the code distance is not odd.
    ValueError
        If the anchor qubit is not a data qubit on the provided grid.
    ValueError
        If the number of data qubits in the code is not correct for the code distance,
        indicating that the patch does not fit onto the grid.
    """

    def __init__(
        self,
        distance: int,
        qubit_grid: HexagonalGrid,
        anchor: QubitCoordinate,
    ) -> None:
        super().__init__(code_distance=distance, qubit_grid=qubit_grid, anchor=anchor)
        self.distance = distance
        if self.distance % 2 == 0:
            raise ValueError(
                "Code distance must be an odd integer, received d=", self.distance
            )

        def in_code(qubit: QubitCoordinate) -> bool:
            """Determine if the given qubit coordinate exists within the confines
            of the code on the grid.

            This is done by first displacing the qubit by it's anchor, effectively
            re-originating it. Then, we check if its (x, y) coordinate satisfy
            the condition that, as we increase the row of the data qubit within
            the triangular color code, the permissable columns become restricted.

            Parameters
            ----------
            qubit : QubitCoordinate
                Qubit coordinate to check

            Returns
            -------
            bool
                Whether or not the qubit is in the code.
            """
            displaced: QubitCoordinate = QubitCoordinate(
                qubit.x - self.anchor.x, qubit.y - self.anchor.y
            )

            within_relevant_rows: bool = (
                0 <= displaced.y <= (self.distance + self.distance // 2)
            )
            within_relevant_columns: bool = (
                max(0, displaced.y / 2)
                <= displaced.x
                < ((self.distance + self.distance // 2) - (max(0, displaced.y / 2)))
            )
            return within_relevant_rows and within_relevant_columns

        self.data_qubits: list[QubitCoordinate] = list(
            filter(in_code, self.qubit_grid.data_qubits)
        )
        if len(self.data_qubits) != _num_data_qubits_in_triangular_color_code(
            distance=self.distance
        ):
            min_dim = self.distance + self.distance // 2
            raise ValueError(
                f"""Invalid number of data qubits! 
                It's possible that your grid size is too small.
                For code distance {self.distance} you require a grid of dimension
                {(min_dim, min_dim)} at least. Your anchor qubit could also
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
        return (
            f"TriangularColorCode(d={self.distance}) @ {self.anchor} on "
            f"{self.qubit_grid.__class__.__name__}"
            f"({self.qubit_grid._x_lim, self.qubit_grid._y_lim})"
        )

    def draw(
        self,
        stabilizer_color_map: Optional[dict[str, list[QubitCoordinate]]] = None,
        figsize: tuple[int, int] = (10, 8),
        indices: bool = True,
        show_all_data_qubits: bool = False,
    ) -> matplotlib.figure.Figure:
        stabilizer_color_map = stabilizer_color_map or {
            "red": self.red_qubits,
            "blue": self.blue_qubits,
            "green": self.green_qubits,
        }
        return super().draw(
            stabilizer_color_map=stabilizer_color_map,
            figsize=figsize,
            indices=indices,
            show_all_data_qubits=show_all_data_qubits,
        )
