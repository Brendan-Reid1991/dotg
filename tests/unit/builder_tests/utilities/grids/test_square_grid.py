import pytest
import ast
from builder.utilities.grids import SquareGrid
from builder.utilities import QubitCoordinate

path = "tests/unit/builder_tests/utilities/grids/grid_data/"


def get_data(x: int, y: int) -> tuple[
    list[QubitCoordinate],
    list[QubitCoordinate],
    list[QubitCoordinate],
    dict[QubitCoordinate, int],
]:
    with open(f"{path}SquareGrid{x}x{y}.txt", "r") as _f:
        return map(ast.literal_eval, _f.readlines())


class TestSquareGrid:
    def test_displacer_values(self):
        assert SquareGrid.Displacer.TOP_RIGHT == (0.5, 0.5)
        assert SquareGrid.Displacer.TOP_LEFT == (-0.5, 0.5)
        assert SquareGrid.Displacer.BOTTOM_RIGHT == (0.5, -0.5)
        assert SquareGrid.Displacer.BOTTOM_LEFT == (-0.5, -0.5)

    @pytest.fixture(scope="class")
    def grid3x3(self) -> SquareGrid:
        return SquareGrid(3, 3)

    @pytest.fixture(scope="class")
    def grid6x6(self) -> SquareGrid:
        return SquareGrid(6, 6)

    @pytest.fixture(scope="class")
    def grid20x5(self) -> SquareGrid:
        return SquareGrid(20, 5)

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_data_qubits(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        data, _, _, _ = get_data(square_grid._x_lim, square_grid._y_lim)
        assert square_grid.data_qubits == data

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_x_stabilizers(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        _, x_stab, _, _ = get_data(square_grid._x_lim, square_grid._y_lim)
        assert square_grid.x_stabilizers == x_stab

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_z_stabilizers(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        _, _, z_stab, _ = get_data(square_grid._x_lim, square_grid._y_lim)
        assert square_grid.z_stabilizers == z_stab

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_coordinate_mapping(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        _, _, _, coord_map = get_data(square_grid._x_lim, square_grid._y_lim)
        assert square_grid.coordinate_mapping == coord_map

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_schedules(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        assert square_grid.schedules == {
            "x": [
                SquareGrid.Displacer.TOP_LEFT,
                SquareGrid.Displacer.TOP_RIGHT,
                SquareGrid.Displacer.BOTTOM_LEFT,
                SquareGrid.Displacer.BOTTOM_RIGHT,
            ],
            "z": [
                SquareGrid.Displacer.TOP_LEFT,
                SquareGrid.Displacer.BOTTOM_LEFT,
                SquareGrid.Displacer.TOP_RIGHT,
                SquareGrid.Displacer.BOTTOM_RIGHT,
            ],
        }

    @pytest.mark.parametrize(
        "grid, stabilizer, neighbours",
        [
            ["grid3x3", (1.5, 0.5), [(1, 1), (2, 1)]],
            ["grid3x3", (1.5, 1.5), [(1, 2), (1, 1), (2, 2), (2, 1)]],
            ["grid6x6", (4.5, 3.5), [(4, 4), (5, 4), (4, 3), (5, 3)]],
            ["grid6x6", (5.5, 2.5), [(5, 3), (5, 2)]],
            ["grid20x5", (2.5, 2.5), [(2, 3), (2, 2), (3, 3), (3, 2)]],
            ["grid20x5", (17.5, 1.5), [(17, 2), (17, 1), (18, 2), (18, 1)]],
            ["grid20x5", (8.5, 3.5), [(8, 4), (9, 4), (8, 3), (9, 3)]],
        ],
    )
    def test_stabilizer_data_qubit_groups(self, grid, stabilizer, neighbours, request):
        square_grid = request.getfixturevalue(grid)
        assert square_grid.stabilizer_data_qubit_groups(stabilizer) == neighbours

    def test_stabilizer_data_qubit_groups_raises_error_for_invalid_stabilizer(
        self, grid3x3
    ):
        for q in grid3x3.data_qubits:
            with pytest.raises(ValueError, match=r"Invalid stabilizer provided:*."):
                grid3x3.stabilizer_data_qubit_groups(q)

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_data_qubit_length_and_format(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        dqs = square_grid._get_data_qubits()
        assert all(q.x == int(q.x) and q.y == int(q.y) for q in dqs)
        assert len(dqs) == (square_grid._x_lim - 1) * (square_grid._y_lim - 1)

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_x_stabilizer_length_and_format(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        x_stabs = square_grid._get_x_stabilizers()
        assert all(q.x != int(q.x) and q.y != int(q.y) for q in x_stabs)

        disallowed = [
            (0, 0),
            (0, square_grid._y_lim - 1),
            (square_grid._x_lim - 1, 0),
            (square_grid._x_lim - 1, square_grid._y_lim - 1),
        ]
        total_x_stabilizers = sum(
            [
                1
                for j in range(square_grid._y_lim)
                for i in range(1 if j % 2 == 0 else 0, square_grid._x_lim, 2)
                if (i, j) not in disallowed
            ]
        )
        assert len(x_stabs) == total_x_stabilizers

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_z_stabilizer_length_and_format(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        x_stabs = square_grid._get_z_stabilizers()
        assert all(q.x != int(q.x) and q.y != int(q.y) for q in x_stabs)

        disallowed = [
            (0, 0),
            (0, square_grid._y_lim - 1),
            (square_grid._x_lim - 1, 0),
            (square_grid._x_lim - 1, square_grid._y_lim - 1),
        ]
        total_z_stabilizers = sum(
            [
                1
                for j in range(square_grid._y_lim)
                for i in range(0 if j % 2 == 0 else 1, square_grid._x_lim, 2)
                if (i, j) not in disallowed
            ]
        )
        assert len(x_stabs) == total_z_stabilizers

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_coordinate_mapping_format(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        assert all(
            isinstance(x, QubitCoordinate) for x in square_grid.coordinate_mapping.keys()
        )
        assert all(isinstance(x, int) for x in square_grid.coordinate_mapping.values())

    @pytest.mark.parametrize("grid", ["grid3x3", "grid6x6", "grid20x5"])
    def test_output_from_initialize(self, grid, request):
        square_grid = request.getfixturevalue(grid)
        data_qubits, x_stabilizers, z_stabilizers, coord_map = get_data(
            square_grid._x_lim, square_grid._y_lim
        )
        assert square_grid._initialize() == (
            data_qubits,
            x_stabilizers,
            z_stabilizers,
            coord_map,
        )
