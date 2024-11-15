"""Define physical qubits on the rotated surface code."""

from typing import Optional
import matplotlib
from builder.patches._patch import Patch
from builder.utilities import QubitCoordinate
from builder.utilities.grids import SquareGrid


class RotatedSurfaceCode(Patch):
    """A patch class for defining a logical qubit on the rotated surface code.

    Provide the code distance as an (d_X, d_Z) tuple, the qubit grid to define the qubit
    on and the 'anchor' qubit which will designate the bottom left hand corner data
    qubit.

    d_X will decide how many _rows_ of data qubits to add, as the top and bottom
    boundaries are X boundaries.

    d_Z will decide how many _columns_ of data qubits to add, as the left and right
    boundaries are Z boundaries.

    Parameters
    ----------
    code_distance: tuple[int, int]
        Code distances as a (d_X, d_Z) tuple.
    qubit_grid: SquareGrid
        SquareGrid class that has data qubits and stabilizers pre-defined.
    anchor: QubitCoordinate
        The anchor qubit, defines the data qubit in the lower left hand corner
        of the patch.

    Attributes
    ----------
    data_qubits: list[QubitCoordinate]
        The list of data qubits in this patch.
    x_stabilizers: list[QubitCoordinate]
        The list of x stabilizer qubits in this patch.
    z_stabilizers: list[QubitCoordinate]
        The list of z stabilizer qubits in this patch.
    """

    def __init__(
        self,
        code_distance: tuple[int, int],
        qubit_grid: SquareGrid,
        anchor: QubitCoordinate | tuple[float, float],
    ) -> None:
        super().__init__(
            code_distance=code_distance, qubit_grid=qubit_grid, anchor=anchor
        )
        self.x_distance, self.z_distance = code_distance

        self.data_qubits: list[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.data_qubits
            if 0 <= coord.x - self.anchor.x < self.z_distance
            and 0 <= coord.y - self.anchor.y < self.x_distance
        ]

        self.x_stabilizers: list[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.x_stabilizers
            if 0 <= coord.x - self.anchor.x < self.z_distance - 1
            and -1 <= coord.y - self.anchor.y < self.x_distance
        ]

        self.z_stabilizers: list[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.z_stabilizers
            if -1 <= coord.x - self.anchor.x < self.z_distance
            and 0 <= coord.y - self.anchor.y < self.x_distance - 1
        ]

        if not self.x_distance * self.z_distance == len(self.data_qubits):
            raise ValueError(
                """Invalid number of data qubits in this patch. Have you placed the 
                anchor too close to the edge of the grid?"""
            )

    def __str__(self):
        return (
            f"RotatedSurfaceCode({self.x_distance}, {self.z_distance})"
            f" @ {self.anchor} on "
            f"{self.qubit_grid.__class__.__name__}"
            f"({self.qubit_grid._x_lim, self.qubit_grid._y_lim})"
        )

    @property
    def right_boundary_data(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the data qubits on
        the right hand boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """

        return [
            dq for dq in self.data_qubits if dq.x == self.anchor.x + self.z_distance - 1
        ]

    @property
    def right_boundary_stabilizers(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the stabilizers on
        the right hand boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [
            dq for dq in self.z_stabilizers if dq.x > self.anchor.x + self.z_distance - 1
        ]

    @property
    def left_boundary_data(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the data qubits on
        the left hand boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [dq for dq in self.data_qubits if dq.x == self.anchor.x]

    @property
    def left_boundary_stabilizers(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the stabilizers on
        the left hand boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [dq for dq in self.z_stabilizers if dq.x < self.anchor.x]

    @property
    def top_boundary_data(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the data qubits on
        the top boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [
            dq for dq in self.data_qubits if dq.y == self.anchor.y + self.x_distance - 1
        ]

    @property
    def top_boundary_stabilizers(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the stabilizers on
        the top boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [
            dq for dq in self.x_stabilizers if dq.y > self.anchor.y + self.x_distance - 1
        ]

    @property
    def bottom_boundary_data(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the data qubits on
        the bottom boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [dq for dq in self.data_qubits if dq.y == self.anchor.y]

    @property
    def bottom_boundary_stabilizers(self) -> list[QubitCoordinate]:
        """Get the qubit coordinates of the stabilizers on
        the bottom boundary of the patch.

        Returns
        -------
        list[QubitCoordinate]
        """
        return [dq for dq in self.x_stabilizers if dq.y < self.anchor.y]

    def draw(
        self,
        stabilizer_color_map: Optional[dict[str, list[QubitCoordinate]]] = None,
        figsize: tuple[int, int] = (10, 8),
        indices: bool = True,
        show_all_data_qubits: bool = False,
    ) -> matplotlib.figure.Figure:
        """Draw the patch on the grid, colouring in the stabilizers
        and optionally adding the indices.

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
        return super().draw(
            stabilizer_color_map=stabilizer_color_map
            or {"red": self.x_stabilizers, "blue": self.z_stabilizers},
            figsize=figsize,
            indices=indices,
            show_all_data_qubits=show_all_data_qubits,
        )
