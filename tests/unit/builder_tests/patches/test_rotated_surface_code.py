import pytest
from ast import literal_eval

from builder.patches._rotated_surface_code import RotatedSurfaceCode
from builder.utilities.grids import SquareGrid

small_grid = SquareGrid(4, 4)
large_grid = SquareGrid(10, 10)
pathway = "tests/unit/builder_tests/patches/patch_data/"


def file_str(code: RotatedSurfaceCode) -> str:
    return (
        pathway
        + f"RSC_d{code.x_distance}{code.z_distance}_grid{code.qubit_grid._x_lim}{code.qubit_grid._y_lim}_anchor{code.anchor[0]}{code.anchor[1]}.txt"
    )


class TestRotatedSurfaceCode:
    @pytest.fixture(scope="class")
    def RSC_d33_grid44_anchor11(self):
        return RotatedSurfaceCode(
            code_distance=(3, 3), qubit_grid=small_grid, anchor=(1, 1)
        )

    @pytest.fixture(scope="class")
    def RSC_d33_grid1010_anchor63(self):
        return RotatedSurfaceCode(
            code_distance=(3, 3), qubit_grid=large_grid, anchor=(6, 3)
        )

    @pytest.fixture(scope="class")
    def RSC_d96_grid1010_anchor11(self):
        return RotatedSurfaceCode(
            code_distance=(9, 6), qubit_grid=large_grid, anchor=(1, 1)
        )

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_stabilizers_and_data_qubits(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        with open(file_str(code), "r") as _f:
            x_stabilizers, z_stabilizers, data_qubits = map(literal_eval, _f.readlines())
        assert (
            x_stabilizers == code.x_stabilizers
        ), f"X stabilizers of code {code} do not match stored data."
        assert (
            z_stabilizers == code.z_stabilizers
        ), f"Z stabilizers of code {code} do not match stored data."
        assert (
            data_qubits == code.data_qubits
        ), f"data qubits of code {code} do not match stored data."

    @pytest.mark.parametrize(
        "distances, grid_size, anchor",
        [
            [(3, 3), (3, 3), (1, 1)],
            [(3, 5), (4, 4), (1, 1)],
            [(3, 5), (6, 4), (3, 2)],
            [(9, 9), (10, 10), (9, 9)],
        ],
    )
    def test_error_raised_for_invalid_distances(self, distances, grid_size, anchor):
        with pytest.raises(ValueError, match="Invalid number of data qubits"):
            RotatedSurfaceCode(
                code_distance=distances, qubit_grid=SquareGrid(*grid_size), anchor=anchor
            )

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_str(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert str(code) == (
            f"RotatedSurfaceCode({code.x_distance}, {code.z_distance})"
            f" @ {code.anchor} on "
            f"{code.qubit_grid.__class__.__name__}"
            f"({code.qubit_grid._x_lim, code.qubit_grid._y_lim})"
        )

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_right_boundary_data(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.right_boundary_data == [
            dq for dq in code.data_qubits if dq.x == code.anchor.x + code.z_distance - 1
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_left_boundary_data(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.left_boundary_data == [
            dq for dq in code.data_qubits if dq.x == code.anchor.x
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_bottom_boundary_data(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.bottom_boundary_data == [
            dq for dq in code.data_qubits if dq.y == code.anchor.y
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_top_boundary_data(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.top_boundary_data == [
            dq for dq in code.data_qubits if dq.y == code.anchor.y + code.x_distance - 1
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_right_boundary_stabilizers(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.right_boundary_stabilizers == [
            dq for dq in code.z_stabilizers if dq.x > code.anchor.x + code.z_distance - 1
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_left_boundary_stabilizers(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.left_boundary_stabilizers == [
            dq for dq in code.z_stabilizers if dq.x < code.anchor.x
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_bottom_boundary_stabilizers(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.bottom_boundary_stabilizers == [
            dq for dq in code.x_stabilizers if dq.y < code.anchor.y
        ]

    @pytest.mark.parametrize(
        "code",
        [
            "RSC_d33_grid44_anchor11",
            "RSC_d33_grid1010_anchor63",
            "RSC_d96_grid1010_anchor11",
        ],
    )
    def test_top_boundary_stabilizers(self, code, request):
        code: RotatedSurfaceCode = request.getfixturevalue(code)
        assert code.top_boundary_stabilizers == [
            dq for dq in code.x_stabilizers if dq.y > code.anchor.y + code.x_distance - 1
        ]
