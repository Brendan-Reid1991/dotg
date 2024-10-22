"""The Visualiser class can be used to draw logical patches."""

from typing import Tuple, Optional, Union, TypeAlias, Literal, get_args
from enum import Enum
import matplotlib
import matplotlib.colors as mpc
import matplotlib.patches
import matplotlib.pyplot as plt

from builder.utilities._qubit_coordinate import QubitCoordinate
from builder.patches.grids import SquareGrid, HexagonalGrid

Grid: TypeAlias = Union[SquareGrid, HexagonalGrid]


class Visualiser:
    """The Visualiser allows qubits to be plotted via matplotlib."""

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
        color: Colors | str,
        opacity: float = STABILIZER_OPACITY,
    ) -> matplotlib.patches.Patch:
        """Draw a stabilizer patch centered on a given coordinate.

        The method returns a Polygon. In the case of a square grid where we require
        weight-2 stabilizers along the boundaries, here we amend the vertex list
        in order to return a rectangle. Rather than using the matplotlib.patches.Rectangle
        class however, we instead simply return a Polygon. This means we must manipulate
        the list to ensure the entire shape is filled.


        Parameters
        ----------
        coordinate : QubitCoordinate
            Coordinate of the stabilizer qubit.
        color : Colors | str
            The color of the stabilizer plaquette.
        opacity : float, optional
            Opacity value, by default STABILIZER_OPACITY

        Returns
        -------
        matplotlib.patches.Patch
            A Polygon Patch object which can be added to an axes.
        """
        vertices = self.grid.stabilizer_data_qubit_groups(stabilizer=coordinate)

        BoundaryT: TypeAlias = Literal["top", "bottom", "left", "right"]

        def _which_boundary(vertex) -> dict[BoundaryT, bool]:
            x, y = vertex
            return {
                "top": abs(y - self.grid._y_lim) <= 1,
                "bottom": abs(y - 0) <= 1,
                "left": abs(x - 0) <= 1,
                "right": abs(x - self.grid._x_lim) <= 1,
            }

        if len(vertices) == 2:
            placement = [
                boundary
                for vertex in vertices
                for boundary, _here in _which_boundary(vertex=vertex).items()
                if _here
            ]

            boundary = next(x for x in placement if placement.count(x) == 2)
            match boundary:
                case "bottom":
                    vertices += [vert + (0, -0.5) for vert in vertices]
                case "top":
                    vertices += [vert + (0, +0.5) for vert in vertices]
                case "left":
                    vertices += [vert + (-0.5, 0) for vert in vertices]
                case "right":
                    vertices += [vert + (+0.5, 0) for vert in vertices]

        sort_qubits = lambda qubits: sorted(qubits, key=lambda x: x[1])
        rectangle = (
            lambda vertex_list: sort_qubits(vertex_list)[0 : len(vertex_list) // 2]
            + sort_qubits(vertex_list)[len(vertex_list) // 2 :][::-1]
        )
        return matplotlib.patches.Polygon(
            xy=rectangle(vertices) if len(vertices) == 4 else vertices,  # type: ignore
            color=color,
            alpha=opacity,
            zorder=1,
            label=coordinate,
        )

    def _qubit_patch(
        self,
        coordinate: QubitCoordinate,
        edgecolor: Colors = Colors.BLACK,
        facecolor: Colors = Colors.WHITE,
        opacity: float = 1.0,
    ) -> matplotlib.patches.Patch:
        """A circle centered over a qubit.

        Parameters
        ----------
        coordinate : QubitCoordinate
            Qubit coordinate.
        edgecolor : Colors, optional
            Edgecolor of the circle, by default Colors.BLACK
        facecolor : Colors, optional
            Facecolor of the circle, by default Colors.WHITE
        opacity : float, optional
            Opacity of the circle, by default 1.0

        Returns
        -------
        matplotlib.patches.Patch
            Circle patch to be added to an axes.
        """
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
    ) -> None:
        """Annotate the figure, by writing text on a given coordinate.

        Parameters
        ----------
        coordinate : QubitCoordinate
            Location of the text box.
        text : str
            Text to add ot the figure.
        color : Colors, optional
            Text color, by default Colors.BLACK
        style : FontStyle, optional
            Text style, by default FontStyle.OBLIQUE
        fontsize : float, optional
            Fontsize, by default 12.5
        opacity : float, optional
            Opacity of the text, by default 1.0.
        """
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
        color: Colors | str,
        fade_index: bool = False,
        opacity: float = 0.4,
    ):
        """Generate a stabilizer patch and add it to the figure.

        Parameters
        ----------
        stabilizer : QubitCoordinate
            Stabilizer coordinate.
        color : Colors | str
            What color to fill the stabilizer.
        fade_index : bool, optional
            Whether or not to fade the index, by default False. If true, sets
            the index to 50% opacity.
        opacity : float, optional
            Overall opacity of the stabilizer plaquette, by default 0.4.
        """
        self.ax.add_patch(
            self._stabilizer(
                coordinate=stabilizer,
                color=color,
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
        """Generate a qubit patch and add it to the figure.

        Parameters
        ----------
        qubit : QubitCoordinate
            Which qubit to draw.
        patch_opacity : float, optional
            Opacity of the circle, by default 1.0
        text_opacity : float, optional
            Opacity of the label, by default 1.0
        """
        self.ax.add_patch(self._qubit_patch(coordinate=qubit, opacity=patch_opacity))
        if self.show_indices:
            self.annotate(coordinate=qubit, text=f"{qubit.idx}", opacity=text_opacity)

    def highlight_qubit(self, qubit: QubitCoordinate, color: Colors):
        """Highlight a qubit by drawing an empty circle around it.

        Parameters
        ----------
        qubit : QubitCoordinate
            Which qubit coordinate to highlight.
        color : Colors
            Which color to highlight it with.
        """
        circle = plt.Circle(
            xy=qubit,
            radius=0.8 * self.CIRCLE_RADII,
            linewidth=2,
            edgecolor=color,
            fill=False,
            zorder=3,
        )
        self.ax.add_patch(circle)
