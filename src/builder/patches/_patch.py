"""A simple base class for a logical qubit patch on a grid."""

from typing import Optional
import matplotlib

from builder.utilities.grids._grid import QubitGrid
from builder.utilities import QubitCoordinate, Visualiser


class Patch:
    def __init__(
        self,
        code_distance: tuple[int, int] | int,
        qubit_grid: QubitGrid,
        anchor: QubitCoordinate | tuple[float, float],
    ) -> None:
        self.code_distance = code_distance
        self.qubit_grid = qubit_grid
        self.anchor = QubitCoordinate(*anchor) if isinstance(anchor, tuple) else anchor

        if self.anchor not in self.qubit_grid.data_qubits:
            raise ValueError(
                f"Invalid anchor: {self.anchor}.\n"
                "The anchor designates the bottom left hand corner data qubit; "
                "chosen anchor is not a data qubit."
                "\nAll data qubit coordinates can be accessed through the "
                f"{self.qubit_grid.__class__.__name__} method 'data_qubits'."
            )

        self.data_qubits: list[QubitCoordinate] = []

    def draw(
        self,
        stabilizer_color_map: Optional[
            dict[str | Visualiser.Colors, list[QubitCoordinate]]
        ] = None,
        figsize: tuple[int, int] = (10, 8),
        indices: bool = True,
        show_all_data_qubits: bool = False,
    ) -> matplotlib.figure.Figure:
        """Draw the patch on the grid, colouring in the stabilizers
        and optionally adding the indices.

        Parameters
        ----------
        stabilizer_color_map: dict[str | Visualiser.Colors, list[QubitCoordinate]], optional
            The stabilizer color map, indicating which stabilizers to draw in what
            color. The default coloring scheme is set in each Patch, by overriding this
            method.
        figsize: tuple[int, int], optional
            The figure size, by default (10, 8).
        indices : bool, optional
            Add index labels to the qubits, by default True

        Returns
        -------
        matplotlib.figure.Figure
            A matplotlib Figure object.
        """
        if not stabilizer_color_map:
            raise ValueError("Specify how you want stabilizers to be colored!")

        vis = Visualiser(grid=self.qubit_grid, figsize=figsize, show_indices=indices)
        for color, qubits in stabilizer_color_map.items():
            for qubit in qubits:
                vis.draw_stabilizer(
                    stabilizer=qubit,
                    color=color,
                    data_qubit_member_check=self.data_qubits,
                )
        data_qubits_to_plot = (
            self.data_qubits if not show_all_data_qubits else self.qubit_grid.data_qubits
        )
        for data_q in data_qubits_to_plot:
            vis.draw_qubit(qubit=data_q)

        return vis.figure
