import pytest

import matplotlib.colors as mpc
import matplotlib.patches
import matplotlib.pyplot as plt
import numpy as np

from builder.utilities._qubit_coordinate import QubitCoordinate
from builder.patches.grids import SquareGrid, HexagonalGrid

from builder.utilities._visualiser import Visualiser


class TestVisualiser:
    def test_constants(self):
        assert Visualiser.STABILIZER_OPACITY == 0.4
        assert Visualiser.CIRCLE_RADII == 0.25

    def test_Colors(self):
        names, values = zip(*Visualiser.Colors._member_map_.items())
        assert set(names) == set(
            [
                "RED",
                "DARKRED",
                "BLUE",
                "DARKBLUE",
                "PURPLE",
                "DARKGREEN",
                "GREEN",
                "BLACK",
                "WHITE",
                "GREY",
            ]
        )

        assert set(map(getattr, values, ["value"] * len(values))) == set(
            [
                "red",
                "darkred",
                "blue",
                "darkblue",
                "purple",
                "darkgreen",
                "green",
                "black",
                "white",
                "grey",
            ]
        )

    def test_FontStyles(self):
        names, values = zip(*Visualiser.FontStyle._member_map_.items())
        assert set(names) == set(["OBLIQUE", "NORMAL", "ITALIC"])
        assert set(map(getattr, values, ["value"] * len(values))) == set(
            ["oblique", "normal", "italic"]
        )

    @pytest.fixture(scope="class")
    def dummy_square_grid_vis(self) -> Visualiser:
        return Visualiser(grid=SquareGrid(3, 3))

    @pytest.mark.parametrize("color", ["red", "green", "blue"])
    @pytest.mark.parametrize("opacity", [0.1, 0.2, 0.3, 0.4])
    def test_stabilizer_returns_patch_object_with_correct_attrs(
        self, dummy_square_grid_vis, color, opacity
    ):
        patch = dummy_square_grid_vis._stabilizer(
            coordinate=QubitCoordinate(1.5, 1.5),
            data_qubit_member_check=[
                QubitCoordinate(1, 2),
                QubitCoordinate(2, 1),
                QubitCoordinate(2, 2),
            ],
            color=color,
            opacity=opacity,
        )
        assert patch.get_facecolor() == mpc.to_rgba(color, opacity)
        assert patch.get_zorder() == 1
        assert (patch.get_verts() == np.asarray([[2, 1], [2, 2], [1, 2], [2, 1]])).all()

    @pytest.mark.parametrize(
        "grid", [SquareGrid(3, 3), SquareGrid(5, 5), SquareGrid(9, 11), SquareGrid(6, 4)]
    )
    def test_visualiser_smoke(self, grid: SquareGrid):
        vis = Visualiser(grid)
        for stabilizer in grid.x_stabilizers:
            vis.draw_stabilizer(
                stabilizer=stabilizer,
                color=Visualiser.Colors.DARKGREEN,
                data_qubit_member_check=grid.data_qubits,
                fade_index=True,
                opacity=0.555,
            )
        for qubit in grid.data_qubits:
            vis.draw_qubit(qubit=qubit, patch_opacity=0.5, text_opacity=0.2)
            vis.highlight_qubit(qubit=qubit, color="red")
        assert vis.figure
