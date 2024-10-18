from typing import Optional
import numpy as np
from enum import Enum
import ast
import matplotlib
import matplotlib.pyplot as plt

from builder.utilities import QubitCoordinate


class HexagonalGrid:
    class Displacer(Enum):
        NE: tuple[float, float] = (0.5, 1)
        E: tuple[float, float] = (1, 0)
        SE: tuple[float, float] = (0.5, -1)
        SW: tuple[float, float] = (-0.5, -1)
        W: tuple[float, float] = (-1, 0)
        NW: tuple[float, float] = (-0.5, 1)

    def __init__(self, code_distance: int, anchor: QubitCoordinate) -> None:
        self._N = code_distance + code_distance // 2
        self.anchor = QubitCoordinate(*anchor)
        qubits = []
        for y in np.arange(0, self._N):
            for x in np.arange(y / 2, self._N - y / 2):
                qubits.append(QubitCoordinate(x, y))

        self.red_qubits = [
            q for q in qubits if q.y == 0 and q.x in np.arange(1, self._N, 3)
        ]
        self.blue_qubits = [
            q for q in qubits if q.y == 1 and q.x in np.arange(2.5, self._N, 3)
        ]
        self.green_qubits = [
            q for q in qubits if q.y == 2 and q.x in np.arange(1, self._N, 3)
        ]
        for color in [self.red_qubits, self.blue_qubits, self.green_qubits]:
            additions = []
            for q in color:
                while True:
                    q = q + (1.5, 3)
                    if q in qubits:
                        additions.append(q)
                        continue
                    break
            color += additions
        self.data_qubits = [
            q
            for q in qubits
            if q not in self.red_qubits + self.blue_qubits + self.green_qubits
        ]

        self.red_qubits = sorted(self.red_qubits, key=lambda x: (x[1]))
        self.green_qubits = sorted(self.green_qubits, key=lambda x: (x[1]))
        self.blue_qubits = sorted(self.blue_qubits, key=lambda x: (x[1]))

        for idx, q in enumerate(
            self.data_qubits + self.red_qubits + self.blue_qubits + self.green_qubits
        ):
            q.idx = idx

    def _get_neighbour(
        self, stabilizer: QubitCoordinate, displacer: Displacer
    ) -> QubitCoordinate | None:
        neighbour = stabilizer + displacer
        try:
            return next(q for q in self.data_qubits if q == neighbour)
        except StopIteration:
            return None

    def stabilizer_data_qubit_groups(
        self, stabilizer: QubitCoordinate
    ) -> list[QubitCoordinate]:
        data_qubits = []
        for displacement in ColorCodePatch.Displacer._value2member_map_:
            q = self._get_neighbour(stabilizer, displacement)
            if q:
                data_qubits.append(q)

        return data_qubits

    def to_stabilizers(
        self, return_logical: Optional[str] = None
    ) -> tuple[list[str], list[str], str] | tuple[list[str], list[str]]:
        xs = []
        zs = []
        for stabilizer in self.red_qubits + self.green_qubits + self.blue_qubits:
            data_qubits = self.stabilizer_data_qubit_groups(stabilizer=stabilizer)
            for _type in ["X", "Z"]:
                template = ["_"] * len(self.data_qubits)
                for dq in data_qubits:
                    template[dq.idx] = _type
                if _type == "X":
                    xs.append("".join(template))
                else:
                    zs.append("".join(template))
        if return_logical:
            logical = "".join([return_logical] * len(self.data_qubits))
            return xs, zs, logical
        return xs, zs

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
            fig, ax = plt.subplots(1, 1, figsize=(15, 12))

        def draw_data_qubit(data_qubit: QubitCoordinate) -> matplotlib.patches.Patch:
            """Draw a circle where this data qubit should be.

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
                zorder=3,
            )

        def draw_polygon(stabilizer: QubitCoordinate) -> matplotlib.patches.Patch:
            color = (
                "red"
                if stabilizer in self.red_qubits
                else "green"
                if stabilizer in self.green_qubits
                else "blue"
            )
            return matplotlib.patches.Polygon(
                xy=self.stabilizer_data_qubit_groups(stabilizer=stabilizer),
                color=color,
                alpha=0.4,
                zorder=2,
                snap=True,
                label=stabilizer,
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
            for i in range(self._N):
                ax.vlines(
                    i,
                    0,
                    self._N,
                    colors="black",
                    linestyles="dashed",
                    alpha=0.1,
                    zorder=1,
                )
            for j in range(self._N):
                ax.hlines(
                    j,
                    0,
                    self._N,
                    colors="black",
                    linestyles="dashed",
                    alpha=0.1,
                    zorder=1,
                )
            return ax

        ax = draw_grid(ax=ax)
        for qubit in (
            self.data_qubits + self.green_qubits + self.red_qubits + self.blue_qubits
        ):
            if qubit in self.data_qubits:
                patch = draw_data_qubit(data_qubit=qubit)
            else:
                patch = draw_polygon(stabilizer=qubit)
            ax.add_patch(patch)
            if indices:
                polygon: bool = isinstance(patch, matplotlib.patches.Polygon)
                if polygon:
                    xy = ast.literal_eval(patch._label)

                else:
                    xy = patch.center
                ax.annotate(
                    f"{str(qubit.idx)}",
                    xy=xy,
                    color="black",
                    style="oblique",
                    fontsize=17.5,
                    ha="center",
                    va="center",
                )

        plt.gca().set_aspect("equal")

        ax.tick_params(which="both", width=2)
        ax.tick_params(which="major", length=7)
        # ax.tick_params(which="minor", length=4)

        return fig
