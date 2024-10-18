from typing import Dict, List, Tuple, Optional
import matplotlib.axes
import matplotlib.figure
import matplotlib.patches
import matplotlib.pyplot as plt
import matplotlib


from builder.utilities import QubitCoordinate
from builder.patches.grids._square_grid import SquareGrid
from builder.utilities._pauliproduct import PauliProduct


class Patch:
    """A Patch class for defining logical qubits.

    Provide the code distance as an (d_X, d_Z) tuple, the qubit grid to define the qubit on and the 'anchor' qubit which will designate the bottom
    left hand corner data qubit.

    d_X will decide how many _rows_ of data qubits to add, as the top and bottom boundaries are X boundaries.

    d_Z will decide how many _columns_ of data qubits to add, as the left and right boundaries are Z boundaries.

    Parameters
    ----------
    code_distance: Tuple[int, int]
        Code distances as a (d_X, d_Z) tuple.
    qubit_grid: QubitGrid
        QubitGrid class that has data qubits and stabilizers pre-defined.
    anchor: QubitCoordinate
        The anchor qubit, defines the data qubit in the lower left hand corner
        of the patch.

    Attributes
    ----------
    data_qubits: List[QubitCoordinate]
        The list of data qubits in this patch.
    x_stabilizers: List[QubitCoordinate]
        The list of x stabilizer qubits in this patch.
    z_stabilizers: List[QubitCoordinate]
        The list of z stabilizer qubits in this patch.
    """

    def __init__(
        self,
        code_distance: Tuple[int, int],
        qubit_grid: QubitGrid,
        anchor: QubitCoordinate,
    ) -> None:
        self.qubit_grid = qubit_grid
        self.x_distance, self.z_distance = code_distance
        self.anchor = QubitCoordinate(*anchor) if isinstance(anchor, tuple) else anchor

        self.data_qubits: List[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.data_qubits
            if 0 <= coord.x - self.anchor.x < self.z_distance
            and 0 <= coord.y - self.anchor.y < self.x_distance
        ]

        self.x_stabilizers: List[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.x_stabilizers
            if 0 <= coord.x - self.anchor.x < self.z_distance - 1
            and -1 <= coord.y - self.anchor.y < self.x_distance
        ]

        self.z_stabilizers: List[QubitCoordinate] = [
            coord
            for coord in self.qubit_grid.z_stabilizers
            if -1 <= coord.x - self.anchor.x < self.z_distance
            and 0 <= coord.y - self.anchor.y < self.x_distance - 1
        ]

        # Sanity Checks
        if not len(self.data_qubits) - len(self.z_stabilizers + self.x_stabilizers) == 1:
            raise ValueError("Are your dimensions correct? This is not a valid qubit.")

        if not self.x_distance * self.z_distance == len(self.data_qubits):
            raise ValueError(
                "Invalid number of data qubits in this patch. Have you placed the anchor too close to the edge of the grid?"
            )

    def __str__(self):
        return f"Patch({self.x_distance}, {self.z_distance}) @ {self.anchor} on Grid{self.qubit_grid._x_lim, self.qubit_grid._y_lim}"

    @property
    def to_stabilizer_formalism(self) -> Tuple[List[PauliProduct], List[PauliProduct]]:
        return [
            PauliProduct(
                ".".join(
                    [
                        f"X{q.idx}"
                        for q in self.qubit_grid.stabilizer_data_qubit_groups(stab)
                        if q in self.data_qubits
                    ]
                )
            )
            for stab in self.x_stabilizers
        ], [
            PauliProduct(
                ".".join(
                    [
                        f"Z{q.idx}"
                        for q in self.qubit_grid.stabilizer_data_qubit_groups(stab)
                        if q in self.data_qubits
                    ]
                )
            )
            for stab in self.z_stabilizers
        ]

    @property
    def right_boundary_data(self) -> List[QubitCoordinate]:
        return [
            dq for dq in self.data_qubits if dq.x == self.anchor.x + self.z_distance - 1
        ]

    @property
    def right_boundary_stabilizers(self) -> List[QubitCoordinate]:
        return [
            dq for dq in self.z_stabilizers if dq.x > self.anchor.x + self.z_distance - 1
        ]

    @property
    def left_boundary_data(self) -> List[QubitCoordinate]:
        return [dq for dq in self.data_qubits if dq.x == self.anchor.x]

    @property
    def left_boundary_stabilizers(self) -> List[QubitCoordinate]:
        return [dq for dq in self.z_stabilizers if dq.x < self.anchor.x]

    @property
    def top_boundary_data(self) -> List[QubitCoordinate]:
        return [
            dq for dq in self.data_qubits if dq.y == self.anchor.y + self.x_distance - 1
        ]

    @property
    def top_boundary_stabilizers(self) -> List[QubitCoordinate]:
        return [
            dq for dq in self.x_stabilizers if dq.y > self.anchor.y + self.x_distance - 1
        ]

    @property
    def bottom_boundary_data(self) -> List[QubitCoordinate]:
        return [dq for dq in self.data_qubits if dq.y == self.anchor.y]

    @property
    def bottom_boundary_stabilizers(self) -> List[QubitCoordinate]:
        return [dq for dq in self.x_stabilizers if dq.y < self.anchor.y]

    def draw(
        self,
        figure: Optional[matplotlib.figure.Figure] = None,
        indices: bool = False,
    ) -> matplotlib.figure.Figure:
        """Draw the patch on the grid, colouring in the stabilizers and optionally adding the indices.

        Parameters
        ----------
        figure: matplotlib.figure.Figure, optional.
            The matplotlib figure to draw on. If not supplied, one is created.
        indices : bool, optional
            Add index labels to the qubits, by default False

        Returns
        -------
        matplotlib.figure.Figure
            A matplotlib Figure object.
        """

        if figure:
            fig = figure
            ax = figure.axes[0]
        else:
            plt.style.use("fast")
            fig, ax = plt.subplots(1, 1, figsize=(8, 6))

        def draw_data_qubit_box(
            data_qubit: QubitCoordinate,
        ) -> matplotlib.patches.Patch:
            """Draw a box where this data qubit should be.

            Parameters
            ----------
            data_qubit : QubitCoordinate
                Data qubit coordinate.

            Returns
            -------
            matplotlib.patches.Patch
                Patch object to be added to the figure.
            """
            return plt.Circle(
                xy=data_qubit,
                radius=0.25,
                linewidth=1,
                edgecolor="black",
                facecolor="white",
                zorder=2,
            )

        def draw_x_stabilizer(stabilizer: QubitCoordinate) -> matplotlib.patches.Patch:
            """Draw an X stabilizer plaquette, coloured red.

            Parameters
            ----------
            stabilizer : QubitCoordinate
                Stabilizer qubit in the plaquette to draw.

            Returns
            -------
            matplotlib.patches.Patch
                Patch object to be added to the figure.
            """
            width = 1
            anchor = (
                stabilizer + (-0.5, 0)
                if stabilizer.y < self.anchor.y
                else stabilizer + QubitGrid.Displacer.BOTTOM_LEFT.value
            )
            height = (
                1
                if self.anchor.y < stabilizer.y < self.x_distance + self.anchor.y - 1
                else 0.5
            )
            return plt.Rectangle(anchor, width, height, color="red", alpha=0.4, zorder=2)

        def draw_z_stabilizer(stabilizer: QubitCoordinate) -> matplotlib.patches.Patch:
            """Draw a Z stabilizer plaquette, coloured blue.

            Parameters
            ----------
            stabilizer : QubitCoordinate
                Stabilizer qubit in the plaquette to draw.

            Returns
            -------
            matplotlib.patches.Patch
                Patch object to be added to the figure.
            """
            width = (
                1
                if self.anchor.x < stabilizer.x < self.z_distance + self.anchor.x - 1
                else 0.5
            )
            height = 1
            anchor = (
                stabilizer + (0, -0.5)
                if stabilizer.x < self.anchor.x
                else stabilizer + QubitGrid.Displacer.BOTTOM_LEFT.value
            )
            return plt.Rectangle(
                anchor, width, height, color="blue", alpha=0.4, zorder=2
            )

        def draw_grid(ax: matplotlib.axes.Axes) -> matplotlib.axes.Axes:
            """Add a grid to the figure, to guide the eye.

            Parameters
            ----------
            ax : matplotlib.axes.Axes
                Figure axis.

            Returns
            -------
            matplotlib.axes.Axes
                The same axis, but now with gridlines.
            """
            for i in range(self.qubit_grid._x_lim + 2):
                ax.vlines(
                    i,
                    0,
                    self.qubit_grid._y_lim + 1,
                    colors="black",
                    linestyles="dashed",
                    alpha=0.1,
                    zorder=1,
                )
            for j in range(self.qubit_grid._y_lim + 2):
                ax.hlines(
                    j,
                    0,
                    self.qubit_grid._x_lim + 1,
                    colors="black",
                    linestyles="dashed",
                    alpha=0.1,
                    zorder=1,
                )
            return ax

        ax = draw_grid(ax=ax)
        for qubit in self.x_stabilizers + self.z_stabilizers + self.data_qubits:
            if qubit in self.data_qubits:
                patch = draw_data_qubit_box(data_qubit=qubit)
            if qubit in self.x_stabilizers:
                patch = draw_x_stabilizer(stabilizer=qubit)
            if qubit in self.z_stabilizers:
                patch = draw_z_stabilizer(stabilizer=qubit)
            ax.add_patch(patch)
            if indices:
                rectangle: bool = isinstance(patch, matplotlib.patches.Rectangle)
                x, y = patch.get_xy() if rectangle else patch.center
                width = patch.get_width()
                height = patch.get_height()
                ax.annotate(
                    f"{str(qubit.idx)}",
                    xy=(x + width / 2, y + height / 2) if rectangle else (x, y),
                    color="black",
                    style="oblique",
                    fontsize=12.5,
                    ha="center",
                    va="center",
                )

        plt.gca().set_aspect("equal")

        ax.tick_params(which="both", width=2)
        ax.tick_params(which="major", length=7)
        # ax.tick_params(which="minor", length=4)

        return fig
