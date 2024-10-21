"""The Visualiser class can be used to draw logical patches."""

from typing import Tuple, Optional, Union, TypeAlias
from enum import Enum
import matplotlib
import matplotlib.colors as mpc
import matplotlib.patches
import matplotlib.pyplot as plt

from builder.utilities._qubit_coordinate import QubitCoordinate
from builder.patches.grids import SquareGrid, HexagonalGrid

Grid: TypeAlias = Union[SquareGrid, HexagonalGrid]


class Visualiser:

    STABILIZER_OPACITY: float = 0.4
    CIRCLE_RADII: float = 0.25

    class Colors(str, Enum):
        RED = "red"
        DARKRED = "darkred"
        BLUE = "blue"
        DARKBLUE = "blue"
        PURPLE = "purple"
        DARKGREEN = "darkgreen"
        GREEN = "green"
        BLACK = "black"
        WHITE = "white"
        GREY = "grey"

    class FontStyle(str, Enum):
        OBLIQUE = "oblique"
        NORMAL = "normal"
        ITALIC = "italic"

    def __init__(
        self,
        grid: Grid,
        figsize: Tuple[int, int] = (10, 8),
        show_indices: bool = True,
    ):
        self.grid = grid
        self.figure, self.ax = plt.subplots(1, 1, figsize=figsize)
        self.ax.set_aspect("equal")
        self.ax.tick_params(which="both", width=2)
        self.ax.tick_params(which="major", length=7)
        self._gridlines()
        self.show_indices = show_indices

    def _gridlines(self):
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
        for i in range(self.grid._x_lim + 1):
            self.ax.vlines(
                i,
                0,
                self.grid._y_lim,
                colors="black",
                linestyles="dashed",
                alpha=0.1,
                zorder=1,
            )
        for j in range(self.grid._y_lim + 1):
            self.ax.hlines(
                j,
                0,
                self.grid._x_lim,
                colors="black",
                linestyles="dashed",
                alpha=0.1,
                zorder=1,
            )

    def _stabilizer(
        self,
        coordinate: QubitCoordinate,
        color: Colors,
        opacity: float = STABILIZER_OPACITY,
    ) -> matplotlib.patches.Patch:
        return matplotlib.patches.Polygon(
            xy=self.grid.stabilizer_data_qubit_groups(stabilizer=coordinate),  # type: ignore
            color=color,
            alpha=opacity,
            zorder=1,
            snap=True,
            label=coordinate,
        )

    def _stabilizer_patch(
        self,
        coordinate: QubitCoordinate,
        color: Colors,
        which_boundary: Optional[str] = None,
        opacity: float = STABILIZER_OPACITY,
    ) -> matplotlib.patches.Patch:
        if which_boundary and which_boundary.lower() not in [
            "top",
            "bottom",
            "left",
            "right",
        ]:
            raise ValueError(
                f"Invalid option for boundary specification: {which_boundary}. Must be one of 'top', 'bottom', 'left', 'right'."
            )
        if which_boundary:
            width = 1 if which_boundary in ["top", "bottom"] else 0.5
            height = 1 if which_boundary in ["left", "right"] else 0.5
            anchor = (
                coordinate + (-0.5, -0.5)
                if which_boundary in ["top", "right"]
                else (
                    coordinate + (-0.5, 0)
                    if which_boundary == "bottom"
                    else coordinate + (0, -0.5)
                )
            )
        else:
            width = 1
            height = 1
            anchor = coordinate + (-0.5, -0.5)
        return plt.Rectangle(anchor, width, height, color=color, alpha=opacity, zorder=1)

    def _qubit_patch(
        self,
        coordinate: QubitCoordinate,
        edgecolor: Colors = Colors.BLACK,
        facecolor: Colors = Colors.WHITE,
        opacity: float = 1.0,
    ) -> matplotlib.patches.Patch:
        return plt.Circle(
            xy=coordinate,
            radius=self.CIRCLE_RADII,
            linewidth=1,
            edgecolor=edgecolor,
            facecolor=facecolor,
            zorder=2,
            alpha=opacity,
        )

    def annotate(
        self,
        coordinate: QubitCoordinate,
        text: str,
        color: Colors = Colors.BLACK,
        style: FontStyle = FontStyle.OBLIQUE,
        fontsize: float = 12.5,
        opacity: float = 1.0,
    ):
        self.ax.annotate(
            text,
            xy=coordinate,
            color=color,
            style=style,
            fontsize=fontsize,
            ha="center",
            va="center",
            alpha=opacity,
            zorder=3,
        )

    def draw_stabilizer(
        self,
        stabilizer: QubitCoordinate,
        color: Colors,
        which_boundary: Optional[str] = None,
        fade_index: bool = False,
        opacity: float = 0.4,
    ):
        self.ax.add_patch(
            self._stabilizer(
                coordinate=stabilizer,
                color=color,
                # which_boundary=which_boundary,
                opacity=opacity,
            )
        )
        if self.show_indices:
            self.annotate(
                coordinate=stabilizer,
                text=f"{stabilizer.idx}",
                opacity=0.5 if fade_index else 1.0,
            )

    def draw_qubit(
        self,
        qubit: QubitCoordinate,
        patch_opacity: float = 1.0,
        text_opacity: float = 1.0,
    ):
        self.ax.add_patch(self._qubit_patch(coordinate=qubit, opacity=patch_opacity))
        if self.show_indices:
            self.annotate(coordinate=qubit, text=f"{qubit.idx}", opacity=text_opacity)

    def highlight_qubit(self, qubit: QubitCoordinate, color: Colors):
        circle = plt.Circle(
            xy=qubit,
            radius=0.8 * self.CIRCLE_RADII,
            linewidth=2,
            edgecolor=color,
            fill=False,
            zorder=3,
        )
        self.ax.add_patch(circle)


if __name__ == "__main__":
    import numpy as np

    grid = HexagonalGrid(x_lim=4, y_lim=4)
    vis = Visualiser(grid=grid, show_indices=True)
    for qub in grid.data_qubits:
        vis.draw_qubit(qubit=qub)
    for qub in grid.red_qubits:
        vis.draw_stabilizer(stabilizer=qub, color=vis.Colors.RED)
    for qub in grid.blue_qubits:
        vis.draw_stabilizer(stabilizer=qub, color=vis.Colors.BLUE)
    for qub in grid.green_qubits:
        vis.draw_stabilizer(stabilizer=qub, color=vis.Colors.GREEN)
    vis.figure.savefig("test.png")
